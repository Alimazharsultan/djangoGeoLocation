# Generated by Django 4.0.4 on 2022-04-25 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unitrack', '0002_unitrackinput'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitrackinput',
            name='geeks_field',
            field=models.DateTimeField(),
        ),
    ]
