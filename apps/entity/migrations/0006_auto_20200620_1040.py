# Generated by Django 3.0.3 on 2020-06-20 10:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0005_dump_scenarioid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='custom',
            name='mentions',
        ),
        migrations.RemoveField(
            model_name='custom',
            name='salience',
        ),
    ]