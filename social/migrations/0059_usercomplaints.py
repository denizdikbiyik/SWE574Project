# Generated by Django 2.2.24 on 2022-04-18 12:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social', '0058_like'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserComplaints',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback', models.TextField(blank=True, null=True)),
                ('isDeleted', models.BooleanField(default=False)),
                ('rated', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complainted', to=settings.AUTH_USER_MODEL, verbose_name='user')),
                ('rater', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='complainter', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
    ]
