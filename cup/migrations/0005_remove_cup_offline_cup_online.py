# Generated by Django 4.0.1 on 2022-03-26 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cup', '0004_cup_offline'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cup',
            name='offline',
        ),
        migrations.AddField(
            model_name='cup',
            name='online',
            field=models.BooleanField(default=False, verbose_name='online?'),
        ),
    ]