# Generated by Django 3.2.12 on 2022-05-04 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0002_badge_type'),
        ('treasuretrack', '0014_auto_20220504_2218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklytreasurelevel',
            name='bonus_badge',
            field=models.ManyToManyField(blank=True, to='badges.Badge'),
        ),
    ]