# Generated by Django 2.2.14 on 2020-07-28 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pingdata',
            name='connection_type',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
