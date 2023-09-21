from django.db import models
from django.urls import reverse_lazy
from django.core.validators import validate_comma_separated_integer_list

from .infrastructure.enums import *


class Superuser(models.Model):
    external_id = models.PositiveIntegerField(verbose_name='Telegram id')


class Profile(models.Model):
    name = models.CharField(verbose_name="Ім'я, Прізвище", max_length=65)
    ordinal = models.SmallIntegerField(verbose_name="Номер в списку")
    journal = models.ForeignKey(to='Journal', on_delete=models.CASCADE, verbose_name="Журнал")
    external_id = models.PositiveIntegerField(verbose_name='Telegram id')

    def get_absolute_url(self):
        return reverse_lazy('profile', kwargs={'news_id': self.pk})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Профіль"
        verbose_name_plural = "Взводи"
        ordering = ['ordinal']


class Journal(models.Model):
    name = models.CharField(verbose_name="Номер взводу", max_length=3, db_index=True)
    strength = models.SmallIntegerField(verbose_name="Чисельність взводу")
    external_id = models.IntegerField(verbose_name="Chat id")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Взвод"
        verbose_name_plural = "Взводи"
        ordering = ['-name']


class JournalEntry(models.Model):
    journal = models.ForeignKey(to='Journal', on_delete=models.CASCADE, verbose_name="Журнал")
    profile = models.ForeignKey(to='Profile', on_delete=models.CASCADE)
    date = models.DateField()
    lesson = models.IntegerField(null=True) #TODO: rename to lesson_ord
    is_present = models.BooleanField(verbose_name="Присутність", null=True)
    status = models.CharField(verbose_name='Статус', max_length=60, null=True)


class ReportParameters(models.Model):
    journal = models.ForeignKey(to='Journal', on_delete=models.CASCADE, verbose_name="Журнал")
    date = models.DateField()
    lessons = models.CharField(validate_comma_separated_integer_list, max_length=15, null=True)
    @property
    def lessons_integer_list(self):
        lessons_list_string = self.lessons
        lessons_string_list = lessons_list_string.replace('[', '').replace(']','').split(',')
        lessons_integer_list = [int(e) for e in lessons_string_list]

        return lessons_integer_list

    mode = models.CharField(max_length=12, choices=Presence.choices, default=default)

#TODO: add a model for schedule using hash-key
#TODO: add a model for lessons

#TODO: add a model for event