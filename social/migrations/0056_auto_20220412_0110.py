# Generated by Django 2.2.24 on 2022-04-12 01:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0055_communication'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventapplication',
            name='isDeleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='serviceapplication',
            name='isDeleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='serviceapplication',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rel_services', to='social.Service'),
        ),
    ]
