# Generated by Django 5.2.1 on 2025-05-10 21:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_tag_avatar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='avatar',
        ),
    ]
