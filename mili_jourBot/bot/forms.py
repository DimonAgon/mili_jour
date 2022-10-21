
from django import forms
from .models import Profile
from django.core import exceptions
import re


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'autofocus': True, 'required': True})
        }

        labels = {
            'name': "Ваше Прізвище та Ім'я, По Батькові"
        }

        def clean_name(self):
            name = self.cleaned_data['name']
            if re.match(pattern="", string=name):
                raise exceptions.ValidationError("Введіть ім'я коректно")
            return name

