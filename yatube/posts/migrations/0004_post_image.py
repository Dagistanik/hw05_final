# Generated by Django 2.2.19 on 2021-12-15 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20211215_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(
                blank=True,
                upload_to='posts/',
                verbose_name='Картинка'
            ),
        ),
    ]
