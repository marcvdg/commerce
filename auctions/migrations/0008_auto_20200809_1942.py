# Generated by Django 3.0.8 on 2020-08-09 19:42

from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_auto_20200809_1828'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bid',
            old_name='bid',
            new_name='amount',
        ),
        migrations.AddField(
            model_name='listing',
            name='watched_by',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bid',
            name='timestamp',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]
