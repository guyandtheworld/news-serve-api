# Generated by Django 3.0.3 on 2020-05-01 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0051_auto_20200430_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='bucket',
            name='description',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]