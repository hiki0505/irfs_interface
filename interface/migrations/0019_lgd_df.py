# Generated by Django 3.2.5 on 2021-08-10 08:50

from django.db import migrations, models
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0018_auto_20210810_1214'),
    ]

    operations = [
        migrations.CreateModel(
            name='LGD_DF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', picklefield.fields.PickledObjectField(editable=False)),
            ],
        ),
    ]