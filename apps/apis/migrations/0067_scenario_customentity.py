# Generated by Django 3.0.3 on 2020-07-04 13:07

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0066_userscenario_access'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenario',
            name='customEntity',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None),
        ),
    ]
