# Generated by Django 2.0.8 on 2019-01-11 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasources', '0021_loosen_unique_metadata'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasource',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
