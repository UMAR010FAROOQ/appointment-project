from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Contact, Service

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'service', 'city', 'country', 'gender')
    search_fields = ('name', 'email', 'service__name', 'city', 'country', 'gender')
    list_filter = ('service', 'gender', 'country', 'city')
    ordering = ('-id',)


admin.site.register(Service)
