# Generated by Django 2.0.8 on 2018-08-21 09:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datasources', '0002_add_access_control_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasource',
            name='users_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='datasource', to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='datasource',
            name='users_group_requested',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='datasource_requested', to='auth.Group'),
        ),
    ]
