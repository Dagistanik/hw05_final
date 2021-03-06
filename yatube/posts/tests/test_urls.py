from django.test import TestCase, Client
from posts.models import User, Group, Post
from django.core.cache import cache


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.group = Group.objects.create(
            title='текстовый заголовок',
            slug='test-slug',
            description='тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = StaticURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_homepage(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_slug(self):
        """Страница /group/slug/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile_username(self):
        """Страница /profile/username/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/test_user/')
        self.assertEqual(response.status_code, 200)

    def test_post_id(self):
        """Страница /posts/post_id/ доступна любому пользователю."""
        post_id = self.post.pk
        response = self.guest_client.get(f'/posts/{ post_id }/')
        self.assertEqual(response.status_code, 200)

    def test_posts_post_id_edit(self):
        """Страница posts/post_id_edit/ доступна только автору"""
        self.assertEqual(self.post.author.username, self.user.username)

    def test_create(self):
        """страница /create/ доступна только авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        """Несуществующая страница"""
        response = self.authorized_client.get('/posts/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_task_list_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_unfollow(self):
        """Проверка страницы unfolow"""
        user = self.user.username
        response = self.authorized_client.get(f'/profile/{ user }/unfollow/')
        self.assertEqual(response.status_code, 302)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/test_user/': 'posts/profile.html',
            '/posts/' + f'{self.post.pk}' + '/': 'posts/post_detail.html',
            '/posts/' + f'{self.post.pk}' + '/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
