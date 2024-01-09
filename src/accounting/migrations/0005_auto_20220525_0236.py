# Generated by Django 3.2.12 on 2022-05-25 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_auto_20220519_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='create_timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created timestamp'),
        ),
        migrations.AlterField(
            model_name='account',
            name='update_timestamp',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated timestamp'),
        ),
        migrations.AlterField(
            model_name='bankmovement',
            name='create_timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created timestamp'),
        ),
        migrations.AlterField(
            model_name='bankmovement',
            name='update_timestamp',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated timestamp'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='create_timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created timestamp'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='update_timestamp',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated timestamp'),
        ),
    ]
