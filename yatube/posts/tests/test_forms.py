from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from posts.models import Post, Group, Comment
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
from django.conf import settings
import shutil


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='admin')
        cls.authorized_client = Client()
        cls.guest_client = Client()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post и происходит редирект"""
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
        form_data = {
            'text': 'Тестовый тескт_1',
            'group': self.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=['admin'])
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/small.gif').exists())

    def test_edit_post(self):
        """Происходит изменение поста"""
        post_id = self.post.pk
        expected_text = 'Изменённый текст'
        form_data = {
            'text': expected_text,
            'group': self.group.pk,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=(str(post_id))),
            data=form_data,
            follow=True
        )
        self.assertTrue(Post.objects.filter(
            text=form_data['text'], group=form_data['group']).exists())

    def test_comment_guest_client(self):
        """Неавторизованный пользователь не может добавить комментарий."""
        post_id = self.post.pk
        comments_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'author': self.user,
            'text': 'Тестовый комментарий'
        }
        self.guest_client.post(
            reverse('posts:add_comment', args=[post_id]),
            data=form_data,
            follow=True
        )
        self.assertEqual(comments_count, Comment.objects.count())
