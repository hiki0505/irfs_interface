# Generated by Django 3.2.5 on 2021-07-16 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0008_auto_20210716_1941'),
    ]

    operations = [
        migrations.AddField(
            model_name='ifrs',
            name='ctype',
            field=models.CharField(default=None, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ifrs',
            name='ptype',
            field=models.CharField(default=None, max_length=255),
            preserve_default=False,
        ),
    ]
