# admin.py
from django.contrib import admin
from .models import Service

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Service, ServiceAdmin)
