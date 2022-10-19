from django.db import models
from django.urls import reverse_lazy


class Profile(models.Model):
    external_id = models.CharField(verbose_name="тег", max_length=65)
    name = models.CharField(verbose_name="Ім'я, Прізвище", max_length=65)
    Journal = models.CharField(verbose_name="Журнал", max_length=65)

    def get_absolute_url(self):
        return reverse_lazy('profile', kwargs={'news_id': self.pk})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Профіль"
        ordering = ['-name']



class JournalEntry(models.Model):
    date = models.DateField()
    name = models.ForeignKey(to='Profile', on_delete=models.CASCADE)
    journal = models.ForeignKey(to='Journal', on_delete=models.CASCADE)

class Journal(models.Model):
    name = models.PositiveIntegerField(verbose_name="Номер взводу")
    external_id = models.PositiveIntegerField()

    def get_absolute_url(self):
        return reverse_lazy('journal', kwargs={'news_id': self.pk})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Журнал"
        ordering = ['-name']