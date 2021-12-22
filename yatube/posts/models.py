from django.db import models
from django.contrib.auth import get_user_model
from .validators import validate_not_empty
import datetime
User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='заглавие',
        help_text='напишите заглавие'
    )
    slug = models.SlugField(
        unique=True,
        max_length=20,
        default='title',
        verbose_name='Slug',
        help_text='Установите slug'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Напишите описание'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Установите дату'
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Автор',
        help_text='Выберите автора'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    text = models.TextField(
        validators=[validate_not_empty],
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        null=True,
        on_delete=models.SET_NULL,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='comments'
    )
    text = models.TextField(
        'Текст',
        help_text='Текст нового комментария'
    )
    created = models.DateTimeField(
        auto_now_add=True
    )

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.SET_NULL,
        null=True
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='Автор',
        on_delete=models.SET_NULL,
        null=True
    )
