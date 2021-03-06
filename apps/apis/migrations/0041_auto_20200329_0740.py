# Generated by Django 3.0.3 on 2020-03-29 07:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0040_auto_20200317_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entityscore',
            name='entityID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.StoryEntityRef'),
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='entityID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entities', to='apis.Entity'),
        ),
        migrations.DeleteModel(
            name='StoryEntities',
        ),
    ]
