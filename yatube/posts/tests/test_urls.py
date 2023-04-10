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

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.follower_client = Client()
        cls.follower_client.force_login(cls.follower)

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
            '/follow/': HTTPStatus.FOUND,
            f'/profile/{self.user}/follow/': HTTPStatus.FOUND,
            f'/profile/{self.user}/unfollow/': HTTPStatus.FOUND,
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
            f'/posts/{self.post.id}/comment/': HTTPStatus.FOUND,
            '/follow/': HTTPStatus.OK,
            f'/profile/{self.user}/follow/': HTTPStatus.FOUND,
            f'/profile/{self.user}/unfollow/': HTTPStatus.NOT_FOUND,
        }
        for page2, status2 in url_pages_authorized.items():
            with self.subTest(page2=page2, status2=status2):
                response_authorized = self.authorized_client.get(page2)
                self.assertEqual(response_authorized.status_code, status2)

    def test_redirects(self):
        """Редирект для неавторизованных пользователей"""
        urls = {
            '/create/': '/auth/login/?next=/create/',
            '/follow/': '/auth/login/?next=/follow/',
            f'/profile/{self.user.username}/follow/':
            f'/auth/login/?next=/profile/{self.user.username}/follow/',
        }
        for url, redirect in urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, redirect)

    def test_profile_follow_redirect_author(self):
        """Редирект если автор подписывается на самого себя"""
        response = self.authorized_client.get(f'/profile/{self.user}/follow/')
        self.assertRedirects(response, '/follow/')
