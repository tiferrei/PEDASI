# Generated by Django 2.0.8 on 2019-01-10 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasources', '0020_merge_20190107_1508'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='metadataitem',
            unique_together={('field', 'datasource', 'value')},
        ),
    ]