from django.contrib import admin
from .models import *

for model in (Superuser, Profile, Journal, JournalEntry, ReportParameters):
    admin.site.register(model)