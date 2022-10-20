
from django import forms
from .models import Profile
import re

name_pattern = re.Pattern('')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('name')
        widgets = {
            'name': forms.TextInput(attrs={'autofocus': True, 'required': True})
        }

        labels = {
            'name': "Ім'я Прізвище По батькові"
        }
        #
        # def clean_name(self):
        #     name = self.cleaned_data['name']
        #     if re.match()
