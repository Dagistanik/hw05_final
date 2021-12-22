from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post, Comment
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django import forms
from django.core.cache import cache
# from django.core.cache.utils import make_template_fragment_key


User = get_user_model()


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text='Тестовый текст кэша',
            author=cls.user,
        )

    def test_index_cache(self):
        # очищаем кеш от других тестов
        cache.clear()
        # делаем запрос
        response = self.client.get(reverse('posts:index'))
        # Проверяем наличие теста поста в ответе
        self.assertIn(self.post, response.context['posts'])
        # Удаляем тестовый пост
        TestCache.post.delete()
        # Проверяем, что он остался в кэше
        response = self.client.get(reverse('posts:index'))
        self.assertIn(TestCache.post.text, response.getvalue().decode('UTF8'))
        # очищаем кэш
        cache.clear()
        # Проверяем, что кэш очищен и текста поста в ответе нет
        response = self.client.get(reverse('posts:index'))
        self.assertNotIn(
            TestCache.post.text, response.getvalue().decode('UTF8')
        )
