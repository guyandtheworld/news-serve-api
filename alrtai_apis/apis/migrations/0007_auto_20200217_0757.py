# Generated by Django 3.0.3 on 2020-02-17 07:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0006_auto_20200217_0702'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LastScraped',
            new_name='LastScrape',
        ),
    ]
