# Generated by Django 3.2.13 on 2022-07-12 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0010_auto_20220711_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='discountcode',
            name='type',
            field=models.CharField(choices=[('FOREVER', 'FOREVER'), ('ONE_MONTH', 'ONE_MONTH'), ('TWO_MONTH', 'TWO_MONTH'), ('SIX_MONTH', 'SIX_MONTH'), ('ONE_YEAR', 'ONE_YEAR')], default='ONE_MONTH', max_length=255),
        ),
    ]
