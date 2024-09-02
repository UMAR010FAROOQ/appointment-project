# admin.py
from django.contrib import admin
from .models import InstructorPasswordChange, Education, InstructorProfileInformation

admin.site.register(InstructorPasswordChange)
admin.site.register(Education)


class InstructorProfileInformationAdmin(admin.ModelAdmin):
    list_display = (
        'instructor',
        'institution_name',
        'work_history_institution',
        'services',
        'specializations',
        'workspace_image',
    )
    list_filter = ('instructor', 'start_date', 'end_date', 'work_history_institution', 'services', 'specializations')
    search_fields = ('instructor__user__email', 'institution_name', 'course', 'work_history_institution', 'services', 'specializations')

admin.site.register(InstructorProfileInformation, InstructorProfileInformationAdmin)