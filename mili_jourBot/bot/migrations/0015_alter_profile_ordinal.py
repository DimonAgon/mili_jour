# Generated by Django 4.1.2 on 2023-08-02 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0014_alter_profile_ordinal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='ordinal',
            field=models.SmallIntegerField(verbose_name='Номер в списку'),
        ),
    ]
