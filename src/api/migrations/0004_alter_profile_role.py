# Generated by Django 3.2.13 on 2022-07-04 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_profile_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('user', 'user'), ('manager', 'manager'), ('guardian', 'guardian'), ('student', 'student'), ('principal', 'principal'), ('teacher', 'teacher'), ('adminTeacher', 'adminTeacher')], default='user', max_length=120),
        ),
    ]