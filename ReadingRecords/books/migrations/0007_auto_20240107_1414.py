# Generated by Django 3.0.4 on 2024-01-07 14:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0006_auto_20240107_1408'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='comments',
            new_name='comment',
        ),
    ]
