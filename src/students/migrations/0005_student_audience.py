# Generated by Django 3.2.12 on 2022-03-23 01:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('audiences', '0001_initial'),
        ('students', '0004_auto_20220322_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='audience',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.PROTECT, to='audiences.audience'),
            preserve_default=False,
        ),
    ]