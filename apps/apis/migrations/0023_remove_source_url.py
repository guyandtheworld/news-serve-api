# Generated by Django 3.0.3 on 2020-02-24 18:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0022_bucket_model_label'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='source',
            name='url',
        ),
    ]