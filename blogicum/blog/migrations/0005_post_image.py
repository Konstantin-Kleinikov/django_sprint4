# Generated by Django 3.2.16 on 2025-03-07 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20250306_0027'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='blogs_images', verbose_name='Изображение'),
        ),
    ]
