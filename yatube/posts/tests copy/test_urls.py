from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Group, Post, User


class PostRoutesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

        cls.follower = User.objects.create_user(username='user')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)

    def test_checking_availability_pages(self):
        """доступность страниц для неавторизованного пользователя."""
        url_pages = {
            '': HTTPStatus.OK,
            f'/posts/{self.post.pk}/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            '/profile/auth/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/': HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for page, status in url_pages.items():
            with self.subTest(page=page, status=status):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, status)

    def test_post_create_edit_only_authorized_user(self):
        """Страница доступна только авторизованому пользователю"""
        url_pages_authorized = {
            '/create/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK,
            f'posts/{self.post.id}/comment/': HTTPStatus.NOT_FOUND,
            'follow/': HTTPStatus.NOT_FOUND,
            'profile/auth/follow/': HTTPStatus.NOT_FOUND,
            'profile/auth/unfollow/': HTTPStatus.NOT_FOUND,
        }
        for page2, status2 in url_pages_authorized.items():
            with self.subTest(page2=page2, status2=status2):
                response_authorized = self.authorized_client.get(page2)
                self.assertEqual(response_authorized.status_code, status2)

    def test_redirects(self):
        """Редирект для неавторизованных пользователей"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')
