# Generated by Django 3.0.3 on 2020-06-19 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0066_userscenario_access'),
        ('entity', '0004_dump_published_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='dump',
            name='scenarioID',
            field=models.ForeignKey(default='a8563fe4-f348-4a53-9c1c-07f47a5f7660', on_delete=django.db.models.deletion.CASCADE, to='apis.Scenario'),
            preserve_default=False,
        ),
    ]
