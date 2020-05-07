# Generated by Django 3.0.3 on 2020-05-07 07:15

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0058_bucket_keywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='keywords',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None),
        ),
    ]
