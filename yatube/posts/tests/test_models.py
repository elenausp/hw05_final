from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post, Comment, Follow, NUM

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.user_follower = User.objects.create_user(username='user_follower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            text="Тестовый комментарий",
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            author=cls.author,
            user=cls.user_follower,
        )

    def test_models_post(self):
        """Проверяем что у моделей пост корректно работает __str__"""
        self.assertEqual(str(self.post), self.post.text[:NUM])

    def test_models_group(self):
        """Проверяем что у групп корректно работает __str__"""
        self.assertEqual(self.group.title, self.group.__str__())

    def test_models_comment(self):
        """Проверяем что у моделей пост корректно работает __str__"""
        self.assertEqual(str(self.comment), self.comment.text[:NUM])

    def test_post_verbose_name(self):
        """Проверка verbose_name у post."""
        field_verbos = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verbos.items():
            with self.subTest(value=value):
                verbose_name = self.post._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)

    def test_post_help_text(self):
        """Проверка help_text у post."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                help_text = self.post._meta.get_field(value).help_text
                self.assertEqual(help_text, expected)

    def test_group_verbose_name(self):
        """Проверка verbose_name у групп."""
        field_verboses = {
            'title': "Название группы",
            'description': "Описание группы",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                verbose_name = self.group._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)

    def test_group_help_text(self):
        """Проверка help_text у групп."""
        field_help_texts = {
            'description': "Опишите группу",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                help_text = self.group._meta.get_field(value).help_text
                self.assertEqual(help_text, expected)

    def test_verbose_name(self):
        field_verboses = [
            (post, 'text', 'Текст поста'),
            (post, 'pub_date', 'Дата публикации'),
            (post, 'author', 'Автор'),
            (post, 'group', 'Группа'),
            (group, 'title', "Название группы"),
            (group, 'description', "Описание группы"),
            (comment, 'post', 'Пост'),
            (comment, 'author', 'Автор'),
            (comment, 'text', 'Текст комментария'),
            (comment, 'created', 'Дата публикации комментария'),
            (follow, 'user', 'Пользователь'),
            (follow, 'author', 'Автор'),
        ]
        for model, name, value in field_verboses:
            with self.subTest(model=model, value=value, name=name):
                verbose_name = self.model._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, name)