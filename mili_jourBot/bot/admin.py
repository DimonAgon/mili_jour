from django.contrib import admin

from .models import Profile

@admin.register(Profile)
class AdminProfile(admin.ModelAdmin):
    list_display = ('journal_id', 'name')

