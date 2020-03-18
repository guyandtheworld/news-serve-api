# Generated by Django 3.0.3 on 2020-03-17 12:54

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0039_auto_20200316_0811'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntityType',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='alias',
            name='entityID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alias', to='apis.Entity'),
        ),
        migrations.CreateModel(
            name='StoryEntityRef',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('typeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.EntityType')),
            ],
        ),
        migrations.CreateModel(
            name='StoryEntityMap',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('entityID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.StoryEntityRef')),
                ('storyID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.Story')),
            ],
        ),
    ]