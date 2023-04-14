import types

from django.test import TestCase
from forms import *


class ProfileFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'name': 'John Smith',
            'journal': '123',
            'ordinal': '4',
            'external_id': '9876'
        }
        form = ProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'name': 'john',
            'journal': '00',
            'ordinal': 'abc',
            'external_id': '9876'
        }
        form = ProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)
        self.assertIn('name', form.errors)
        self.assertIn('journal', form.errors)
        self.assertIn('ordinal', form.errors)



