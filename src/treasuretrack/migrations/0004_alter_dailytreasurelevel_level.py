# Generated by Django 3.2.12 on 2022-04-19 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasuretrack', '0003_alter_dailytreasurelevel_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailytreasurelevel',
            name='level',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
