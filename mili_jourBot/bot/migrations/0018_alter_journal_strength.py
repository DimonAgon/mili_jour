# Generated by Django 4.1.2 on 2023-09-21 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0017_superuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='strength',
            field=models.SmallIntegerField(verbose_name='Чисельність взводу'),
        ),
    ]