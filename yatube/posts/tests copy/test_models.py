from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post, NUM

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
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

    def test_models_post(self):
        """Проверяем что у моделей пост корректно работает __str__"""
        self.assertEqual(str(self.post), self.post.text[:NUM])

    def test_models_group(self):
        """Проверяем что у групп корректно работает __str__"""
        self.assertEqual(self.group.title, self.group.__str__())

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
