# Generated by Django 3.2.5 on 2021-07-16 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0009_auto_20210716_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ifrs',
            name='ctype',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='ifrs',
            name='ptype',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]