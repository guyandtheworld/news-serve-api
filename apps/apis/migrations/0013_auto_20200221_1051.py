# Generated by Django 3.0.3 on 2020-02-21 10:51

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0012_auto_20200221_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='body_analytics',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='story',
            name='title_analytics',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, null=True),
        ),
    ]
