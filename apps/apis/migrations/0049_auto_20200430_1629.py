# Generated by Django 3.0.3 on 2020-04-30 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0048_auto_20200429_1822'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='keywords',
            name='keywords',
        ),
        migrations.AlterField(
            model_name='dashuser',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('demo', 'Demo'), ('retired', 'Retired'), ('unverified', 'Unverified')], max_length=10),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('demo', 'Demo'), ('retired', 'Retired'), ('unverified', 'Unverified')], max_length=10),
        ),
    ]
