# Generated by Django 4.1.2 on 2023-07-31 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0013_remove_report_summary_remove_report_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='ordinal',
            field=models.IntegerField(verbose_name='Номер в списку'),
        ),
    ]
