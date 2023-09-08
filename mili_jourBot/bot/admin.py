from django.contrib import admin

from .models import Superuser

@admin.register(Superuser)
class AdminProfile(admin.ModelAdmin):
    pass
