from django.db import models
from django.urls import reverse_lazy


class Profile(models.Model):
    name = models.CharField(verbose_name="Ім'я, Прізвище", max_length=65)
    ordinal = models.CharField(verbose_name="Номер в списку", max_length=2)
    journal = models.ForeignKey(to='Journal', on_delete=models.CASCADE, verbose_name="Журнал")
    external_id = models.PositiveIntegerField(verbose_name='Telegram id')

    def get_absolute_url(self):
        return reverse_lazy('profile', kwargs={'news_id': self.pk})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Профіль"
        verbose_name_plural = "Взводи"
        ordering = ['name']


class Journal(models.Model):
    name = models.CharField(verbose_name="Номер взводу", max_length=3, db_index=True)
    strength = models.CharField(verbose_name="Чисельність взводу", max_length=2)
    external_id = models.PositiveIntegerField(verbose_name="Chat id")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Взвод"
        verbose_name_plural = "Взводи"
        ordering = ['-name']


class JournalEntry(models.Model):
    journal = models.CharField(max_length=180)
    profile = models.ForeignKey(to='Profile', on_delete=models.CASCADE)
    date = models.DateField()
    lesson = models.IntegerField(null=True)
    is_present = models.BooleanField(verbose_name="Присутність")

# TODO: add a model for schedule using hash-key