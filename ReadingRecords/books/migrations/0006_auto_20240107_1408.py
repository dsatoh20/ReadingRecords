# Generated by Django 3.0.4 on 2024-01-07 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_chat'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='contents',
            new_name='comments',
        ),
    ]
