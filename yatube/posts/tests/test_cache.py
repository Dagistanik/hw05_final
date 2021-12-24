from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Post
from django.urls import reverse
from django.core.cache import cache


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
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertIn(self.post, response.context['posts'])
        TestCache.post.delete()
        response = self.client.get(reverse('posts:index'))
        self.assertIn(
            TestCache.post.text, response.getvalue().decode('UTF8')
        )
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotIn(
            TestCache.post.text, response.getvalue().decode('UTF8')
        )
