# Generated by Django 3.2.12 on 2022-05-18 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djstripe', '0002_initial'),
        ('payments', '0003_auto_20220314_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetail',
            name='customer_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='djstripe.customer'),
        ),
    ]