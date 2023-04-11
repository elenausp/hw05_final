from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post, Comment, Follow, POST_TEXT_LIMIT

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group_title = 'test_group'
        cls.post_text = 'test_post'
        cls.comment_text = 'test_comment'
        cls.user_follower = User.objects.create_user(username='user_follower')
        cls.group = Group.objects.create(
            title=cls.group_title,
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text=cls.post_text,
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            text=cls.comment_text,
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            author=cls.author,
            user=cls.user_follower,
        )

    def test_models_str(self):
        models_values = [
            (self.group, self.group_title),
            (self.post, self.post_text[:POST_TEXT_LIMIT]),
            (self.comment, self.comment_text[:POST_TEXT_LIMIT])
        ]
        for model, expected_value in models_values:
            with self.subTest():
                self.assertEqual(str(model), expected_value)

    def test_verbose_name(self):
        fields_verboses = {
            Post: {
                'text': 'Текст поста',
                'pub_date': 'Дата публикации',
                'author': 'Автор',
                'group': 'Группа',
            },
            Group: {
                'title': "Название группы",
                'description': "Описание группы",
            },
            Comment: {
                'post': 'Пост',
                'author': 'Автор',
                'text': 'Текст комментария',
                'created': 'Дата публикации комментария',
            },
            Follow: {
                'user': 'Пользователь',
                'author': 'Автор',
            },
        }
        for model, value in fields_verboses.items():
            for field, verbose_name in value.items():
                with self.subTest(field=field):
                    response = model._meta.get_field(field).verbose_name
                    self.assertEqual(response, verbose_name)

    def test_help_text(self):
        field_help_text = {
            Post: {
                'text': 'Введите текст поста',
                'group': 'Группа, к которой будет относиться пост',
            },
            Group: {
                'description': 'Опишите группу',
            },
            Comment: {
                'text': 'Введите текст',
            },
        }
        for model, value in field_help_text.items():
            for field, help_text in value.items():
                with self.subTest(field=field):
                    response = model._meta.get_field(field).help_text
                    self.assertEqual(response, help_text)
