# Generated by Django 2.2.24 on 2022-04-23 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0003_service_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_address',
            field=models.TextField(blank=True, null=True),
        ),
    ]
