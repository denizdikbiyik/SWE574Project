# Generated by Django 2.2.24 on 2022-05-04 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0008_search'),
    ]

    operations = [
        migrations.AddField(
            model_name='search',
            name='searchType',
            field=models.TextField(blank=True, null=True),
        ),
    ]