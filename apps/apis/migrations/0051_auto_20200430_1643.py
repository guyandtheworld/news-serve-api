# Generated by Django 3.0.3 on 2020-04-30 16:43

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0050_auto_20200430_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keywords',
            name='keywords',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, size=None),
        ),
    ]