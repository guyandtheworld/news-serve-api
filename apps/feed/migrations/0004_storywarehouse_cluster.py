# Generated by Django 3.0.3 on 2020-05-28 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0003_storywarehouse'),
    ]

    operations = [
        migrations.AddField(
            model_name='storywarehouse',
            name='cluster',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
