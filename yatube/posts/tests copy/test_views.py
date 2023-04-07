import shutil
import tempfile
from django.conf import settings
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_context(self):
        """Шаблон сформирован с правильным контекстом."""
        template = {
            reverse('posts:index'): 'page_obj',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'page_obj',
            reverse('posts:profile',
                    kwargs={'username': self.user}): 'page_obj',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): 'post',
        }

        for value, fount in template.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                page_object = response.context[fount]
                if fount == 'page_obj':
                    self.assertEqual(page_object[0], self.post)
                    self.assertContains(response, '<img')
                elif fount == 'post':
                    self.assertEqual(page_object.pk, self.post.pk)
                    self.assertContains(response, '<img')

    def test_post_create_pages_with_the_right_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        self.assertIn('is_edit', response.context)
        self.assertFalse(response.context['is_edit'])

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_user_pages_with_the_right_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        self.assertTrue(response.context['is_edit'])
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_in_group(self):
        """Проверка на корректное размещение поста на страницах"""
        templates_url_names = [
            '',
            f'/group/{self.group.slug}/',
            '/profile/auth/',
        ]
        for url_name in templates_url_names:
            with self.subTest(url_name=url_name):
                response = self.client.get(url_name)
                posts = response.context['page_obj']
                self.assertIn(self.post, posts)

    def test_page_obj_index(self):
        """Проверка паджинации главной страницы"""
        response = self.authorized_client.get(reverse('posts:index'))
        page_object = response.context['page_obj']
        self.assertEqual(len(page_object), 1)
        self.assertIsInstance(page_object[0], Post)

    def test_page_obj_group_list(self):
        """Проверка паджинации страницы постов"""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PostPagesTests.group.slug})
        )
        page_object = response.context['page_obj']
        self.assertEqual(len(page_object), 1)
        self.assertIsInstance(page_object[0], Post)

    def test_cache_page(self):
        """Кэширование главной страницы"""
        cache_content = self.guest_client.get(reverse('posts:index')).content
        Post.objects.all().delete()
        cache_content2 = self.guest_client.get(reverse('posts:index')).content

        self.assertEqual(cache_content, cache_content2)

        cache.clear()
        cache_content3 = self.guest_client.get(reverse('posts:index')).content

        self.assertNotEqual(cache_content, cache_content3)
