# Generated by Django 3.0.3 on 2020-06-07 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0065_dashuser_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='userscenario',
            name='access',
            field=models.CharField(choices=[('view', 'View'), ('edit', 'Edit')], default='edit', max_length=10),
            preserve_default=False,
        ),
    ]
