# Generated by Django 4.1.2 on 2023-08-02 13:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0015_alter_profile_ordinal'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Report',
            new_name='ReportParameters',
        ),
    ]