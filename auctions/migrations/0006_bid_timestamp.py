# Generated by Django 3.0.8 on 2020-08-06 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auto_20200806_0930'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='timestamp',
            field=models.CharField(default=0, max_length=64),
            preserve_default=False,
        ),
    ]
