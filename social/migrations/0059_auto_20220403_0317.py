# Generated by Django 2.2.24 on 2022-04-03 03:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0058_auto_20220403_0314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceapplication',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rel_services', to='social.Service'),
        ),
    ]
