# Generated by Django 3.0.3 on 2020-05-06 06:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0054_auto_20200501_1657'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entity',
            old_name='entityType',
            new_name='typeID',
        ),
    ]
