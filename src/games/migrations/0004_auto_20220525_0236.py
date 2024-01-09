# Generated by Django 3.2.12 on 2022-05-25 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_alter_game_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='create_timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created timestamp'),
        ),
        migrations.AlterField(
            model_name='game',
            name='update_timestamp',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated timestamp'),
        ),
        migrations.AlterField(
            model_name='gamecategory',
            name='create_timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created timestamp'),
        ),
        migrations.AlterField(
            model_name='gamecategory',
            name='update_timestamp',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated timestamp'),
        ),
    ]