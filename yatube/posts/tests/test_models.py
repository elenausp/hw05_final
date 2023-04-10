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

    def test_verbose_name(self):
        field_verboses = [
            (self.post, 'text', 'Текст поста'),
            (self.post, 'pub_date', 'Дата публикации'),
            (self.post, 'author', 'Автор'),
            (self.post, 'group', 'Группа'),
            (self.group, 'title', "Название группы"),
            (self.group, 'description', "Описание группы"),
            (self.comment, 'post', 'Пост'),
            (self.comment, 'author', 'Автор'),
            (self.comment, 'text', 'Текст комментария'),
            (self.comment, 'created', 'Дата публикации комментария'),
            (self.follow, 'user', 'Пользователь'),
            (self.follow, 'author', 'Автор'),
        ]
        for model, name, value in field_verboses:
            with self.subTest(name=name):
                verbose_name = model._meta.get_field(name).verbose_name
                self.assertEqual(verbose_name, value)

    def test_help_text(self):
        field_help_text = [
            (self.post, 'text', 'Введите текст поста',),
            (self.post, 'group', 'Группа, к которой будет относиться пост'),
            (self.group, 'description', 'Опишите группу'),
            (self.comment, 'text', 'Введите текст'),
        ]
        for model, help_text, value in field_help_text:
            with self.subTest(help_text=help_text):
                help_text_response = model._meta.get_field(help_text).help_text
                self.assertEqual(help_text_response, value)
