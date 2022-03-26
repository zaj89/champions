# Generated by Django 4.0.1 on 2022-03-26 15:47

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cup', '0007_cup_author_alter_cup_declarations'),
    ]

    operations = [
        migrations.AddField(
            model_name='cup',
            name='players',
            field=models.ManyToManyField(related_name='players', to=settings.AUTH_USER_MODEL),
        ),
    ]