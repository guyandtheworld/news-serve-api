# Generated by Django 3.0.3 on 2020-03-01 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0031_remove_source_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='score',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]