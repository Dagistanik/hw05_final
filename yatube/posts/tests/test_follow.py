from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Post


User = get_user_model()


class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text='Тестовый текст подписки',
            author=cls.user,
        )
