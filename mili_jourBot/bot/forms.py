
from django import forms
from .models import Profile
from django.core import exceptions
import re


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'journal', 'ordinal', 'external_id']

        labels = {
            'name': "Ваше Прізвище та Ім'я",
            'ordinal': "Ваш номер у списку"
        }

        def clean_name(self):
            name = self.cleaned_data['name']
            if re.match(pattern="\p{Lu}{1}\p{L}+(?:[- ])?\p{L}*\s\p{Lu}{1}\p{L}+", string=name):
                raise exceptions.ValidationError("Введіть ім'я коректно")
            return name

