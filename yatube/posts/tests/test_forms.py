import shutil
import tempfile
from http import HTTPStatus
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, Comment, Follow, User
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormCreateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='auth',)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Форма создания новой записи в БД валидна"""
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст в форме',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), post_count + 1)

        post_test = Post.objects.latest('id')

        self.assertEqual(form_data['group'], post_test.group.id)
        self.assertEqual(form_data['text'], post_test.text)
        self.assertContains(response, '<img')

    def test_edit_post(self):
        """Валидная форма изменяет запись"""
        form_data = {
            'text': 'Тестовый текст в форме',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(form_data['group'], self.group.id)
        self.assertEqual(form_data['text'], self.post.text)

    def test_create_comment_only_authorized(self):
        """Создание комментария на странице авторизированным пользователем"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'текст комментария',
            'post': self.post.id,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_create_comment_not_authorized_user(self):
        """Создание комментария на странице не авторизованным пользователем"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'текст комментария',
            'post': self.post.id,
        }
        response = self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        redirect = reverse('login') + '?next=' + reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertRedirects(response, redirect)


class FollowFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='author',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )
        cls.user_no_follow = User.objects.create(
            username='no_follow',
        )

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_no_follow = Client()
        cls.authorized_client_no_follow.force_login(cls.user_no_follow)

        cache.clear()
        # Не совсем уверена на каком уровне в данном случае надо
        # проводить очистку кэша

    def test_follow_author(self):
        "Проверка записей у тех кто подписан"
        Follow.objects.create(
            user=self.user,
            author=self.post.author)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        response_follow = self.authorized_client.get(
            reverse('posts:follow_index'),
        )
        response_no_follow = self.authorized_client_no_follow.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(len(response_follow.context['page_obj']), 1)
        self.assertEqual(len(response_no_follow.context['page_obj']), 0)

    def test_unfollow_author(self):
        "Проверка записей у тех кто не подписан"
        Follow.objects.create(
            user=self.user,
            author=self.post.author
        )
        Follow.objects.create(
            user=self.user,
            author=self.post.author
        ).delete()
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 1)
