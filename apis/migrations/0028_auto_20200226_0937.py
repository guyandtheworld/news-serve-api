# Generated by Django 3.0.3 on 2020-02-26 09:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('apis', '0027_auto_20200226_0916'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dashuser',
            name='email',
        ),
        migrations.RemoveField(
            model_name='dashuser',
            name='name',
        ),
        migrations.AddField(
            model_name='dashuser',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]