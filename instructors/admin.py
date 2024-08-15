# admin.py
from django.contrib import admin
from .models import InstructorPasswordChange, Education

admin.site.register(InstructorPasswordChange)
admin.site.register(Education)