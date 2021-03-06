# Generated by Django 3.0.3 on 2020-02-15 13:43

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0004_bucket_bucketweight'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelDetails',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('version', models.SmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('url', models.URLField()),
                ('score', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='BucketModel',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('bucketID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.Bucket')),
                ('modelID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.ModelDetails')),
            ],
        ),
    ]
