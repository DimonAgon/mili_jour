from django.db import models
from django.urls import reverse_lazy
from django.core.validators import validate_comma_separated_integer_list

from .infrastructure.enums import *
from static_text.chat_messages import *
from static_text import chat_messages
from static_text.logging_messages import  *

#TODO: unify code

class Superuser(models.Model):
    external_id = models.PositiveIntegerField(verbose_name='Telegram id')

#TODO: consider adding named base model
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
        verbose_name_plural = "Профілі"
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


class ReportParameters(models.Model):
    journal = models.ForeignKey(to='Journal', on_delete=models.CASCADE, verbose_name="Журнал")
    date = models.DateField()
    mode = models.CharField(max_length=12, choices=PresenceMode.choices, default=default)


class Subject(models.Model):
    journals = models.ManyToManyField(Journal)
    name = models.CharField(verbose_name="Предмет", max_length=30)

    class Meta:
        verbose_name = chat_messages.subject_nom_kw.capitalize()
        verbose_name_plural = chat_messages.subjects_kw.capitalize()

class Lesson(models.Model): #TODO: add related superuser field, for maintaining
    subject = models.ForeignKey(
        subject_kw.capitalize()                            ,
        on_delete=models.CASCADE                           ,
        verbose_name=chat_messages.subject_nom_kw.capitalize()
    )
    ordinal = models.IntegerField(verbose_name=f"№ {chat_messages.subject_nom_kw.capitalize()}")

    def __str__(self):
        return f"{self.ordinal}-{self.subject.name}"

    class Meta:
        verbose_name = chat_messages.lesson_kw.capitalize()
        verbose_name_plural = chat_messages.lessons_nom_kw.capitalize()


class Schedule(models.Model):
    lessons = models.ManyToManyField(Lesson)

    class Meta:
        verbose_name = chat_messages.schedule_nom_kw.capitalize()
        verbose_name_plural = chat_messages.schedules_kw.capitalize()

class CurrentSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)
    date = models.DateField()

class JournalEntry(models.Model):
    journal = models.ForeignKey(to='Journal', on_delete=models.CASCADE, verbose_name="Журнал")
    profile = models.ForeignKey(to='Profile', on_delete=models.CASCADE)
    date = models.DateField()
    lesson = models.ForeignKey(
        to=Lesson                                         ,
        on_delete=models.PROTECT                          ,
        verbose_name=chat_messages.lesson_kw.capitalize() ,
        null= True
    )
    is_present = models.BooleanField(verbose_name="Присутність", null=True)
    status = models.CharField(verbose_name='Статус', max_length=60, null=True)


class PresencePoll(models.Model):
    external_id = models.PositiveIntegerField(verbose_name='Telegram id')


#TODO: add a model for event