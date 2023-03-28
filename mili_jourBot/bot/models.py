from django.db import models
from django.urls import reverse_lazy


class Profile(models.Model):

    name = models.CharField(verbose_name="Ім'я, Прізвище", max_length=65)
    journal = models.ForeignKey(to='Journal', on_delete=models.CASCADE)
    ordinal = models.CharField(verbose_name="Номер в списку", max_length=2)
    external_id = models.IntegerField(verbose_name='Telegram id')

    def get_absolute_url(self):
        return reverse_lazy('profile', kwargs={'news_id': self.pk})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Профіль"
        ordering = ['-name']



class Journal(models.Model):
    external_id = models.IntegerField(verbose_name="Chat id")
    number = models.CharField(verbose_name="Номер взводу", max_length=3)


class JournalEntry(models.Model):
    date = models.DateField()
    name = models.ForeignKey(to='Profile', on_delete=models.CASCADE)
    journal = models.CharField(max_length=180)
