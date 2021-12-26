from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post, Comment, Follow
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django import forms
from django.core.cache import cache


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.groups = []
        for i in range(2):
            group = Group.objects.create(
                title=(f'Тестовая группа{i}'),
                slug=(f'test-slug{i}'),
                description=(f'тестовое описание{i}'),
            )
            cls.groups.append(group)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=('Тестовый текст'),
            group=(Group.objects.get(slug='test-slug0')),
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Dagik')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post_id = str(self.post.pk)
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:slug',
                    kwargs={'slug': 'test-slug0'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'test_user'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': post_id}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': post_id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def correct_context(self, post) -> bool:
        """Шаблоны сформированы с правильным контестом"""
        post_fields = {
            'author': Post.objects.get(pk=post.pk).author,
            'group': Post.objects.get(pk=post.pk).group,
            'text': Post.objects.get(pk=post.pk).text,
            'image': Post.objects.get(pk=post.pk).image,
        }
        for value, expected in post_fields.items():
            with self.subTest(value=value):
                post_field = getattr(post, value)
                self.assertEqual(post_field, expected)
            return True

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        post = response.context['posts'][0]
        self.assertTrue(self.correct_context(post))

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        group_slug = 'test-slug0'
        expected_group = Group.objects.get(slug=group_slug)
        response = self.guest_client.get(
            reverse('posts:slug', args=[group_slug]))
        posts = response.context['posts']
        for post in posts:
            self.assertEqual(post.group, expected_group)
        post0 = response.context['posts'][0]
        self.assertTrue(self.correct_context(post0))

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:profile', args=['test_user']))
        username = response.context['username']
        page_obj = response.context['page_obj']
        post = page_obj[0]
        self.assertEqual(post.author, username)
        self.assertTrue(self.correct_context(post))

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        post_id = (self.post).pk
        response = self.guest_client.get(
            reverse('posts:post_detail', args=[post_id]))
        post = response.context['post']
        self.assertEqual(post.pk, post_id)
        self.assertTrue(self.correct_context(post))

    def test_create_post_edit_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        post_id = self.post.pk
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[post_id]))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_additional_create(self):
        """Дополнительная проверка при создании поста
        на главной странице пройдена.
        """
        response = self.guest_client.get(
            reverse('posts:index'))
        posts = response.context['posts']
        post = self.post
        self.assertIn(post, posts)

    def test_additional_group(self):
        """Дополнительная проверка при создании поста на
        странице группы пройдена.
        """
        response = self.guest_client.get(
            reverse('posts:slug', args=['test-slug0']))
        posts = response.context['posts']
        post = (self.post)
        self.assertIn(post, posts)

    def test_additional_profile(self):
        """Дополнительная проверка при создании поста на
        главной странице пройдена.
        """
        response = self.guest_client.get(
            reverse('posts:profile', args=['test_user']))
        post = response.context['page_obj'][0]
        self.assertEqual(post, self.post)

    def test_no_additional_group(self):
        """Дополнительная проверка что пост не попал в
        группу для которой был предназначен
        """
        response = self.guest_client.get(
            reverse('posts:slug', args=['test-slug1']))
        page_obj = response.context['page_obj']
        self.assertNotIn(self.post, page_obj)

    def test_comment_add_post_detail(self):
        """Проверка что комментарий появляется на странице поста"""
        post_id = self.post.pk
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[post_id]))
        comments = response.context['comments']
        self.assertIn(self.comment, comments)


class TestPaginator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.author = User.objects.create(username="author")
        cls.group = Group.objects.create(
            title=('Тестовая группа'),
            slug=('test-slug0'),
            description=('тестовое описание'),
        )
        cls.posts = []
        for i in range(13):
            post = Post.objects.create(
                author=cls.user,
                text=(f'Тестовый текст{i}'),
                group=(Group.objects.get(slug='test-slug0'))
            )
            cls.posts.append(post)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Dagik')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_paginator(self):
        """Паджинация страницы index работает верно"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_paginator(self):
        """Паджинация страницы group_list работает верно"""
        group_slug = 'test-slug0'
        response = self.client.get(reverse('posts:slug', args=[group_slug]))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(
            reverse('posts:slug', args=[group_slug]) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_paginator(self):
        """Паджинация страницы profile работает верно"""
        response = self.client.get(
            reverse('posts:profile', args=['test_user']))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(
            reverse('posts:profile', args=['test_user']) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class TestPaginatorIndex(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.author = User.objects.create(username="author")
        cls.group = Group.objects.create(
            title=('Тестовая группа'),
            slug=('test-slug0'),
            description=('тестовое описание'),
        )
        cls.posts = []
        for i in range(13):
            post = Post.objects.create(
                author=cls.author,
                text=(f'Тестовый текст{i}'),
                group=(Group.objects.get(slug='test-slug0'))
            )
            cls.posts.append(post)
        Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_follow_index_paginator(self):
        """Паджинация страницы follow_index работает верно"""
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.authorized_client.get(
            reverse('posts:follow_index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_author')
        cls.post = Post.objects.create(
            text='Тестовый текст подписки',
            author=cls.author,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Dagik')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_user_subscription(self):
        """Авторизованный пользователь может подписываться на других
        пользователей.
        """
        self.authorized_client.get(
            reverse('posts:profile_follow', args=[self.author]))
        following = Follow.objects.filter(author=self.author).exists()
        self.assertTrue(following)

    def test_unsubscribing_users(self):
        """Авторизованный пользователь может удалять других пользователей
        из подписок.
        """
        Follow.objects.create(author=self.author, user=self.user)
        self.authorized_client.get(
            reverse('posts:profile_unfollow', args=[self.author.username]))
        following = Follow.objects.filter(author=self.author).exists()
        self.assertFalse(following)

    def test_adding_subscriptions_feed(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан.
        """
        self.authorized_client.get(
            reverse('posts:profile_follow', args=[self.author]))
        post = Post.objects.create(
            text='Тестовый текст появление записи',
            author=self.author,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'])

    def test_not_adding_subscriptions_feed(self):
        """Новая запись пользователя не появляется в ленте тех, кто не
        подписан.
        """
        post = Post.objects.create(
            text='Тестовый текст появление записи',
            author=self.author,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'])
