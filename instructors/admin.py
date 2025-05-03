# admin.py
from django.contrib import admin
from .models import InstructorPasswordChange, Education, InstructorProfileInformation, AvailableTimeSlot
from django import forms

admin.site.register(InstructorPasswordChange)
admin.site.register(Education)


class AvailableTimeSlotAdminForm(forms.ModelForm):
    class Meta:
        model = AvailableTimeSlot
        fields = '__all__'
        widgets = {
            'start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }

@admin.register(AvailableTimeSlot)
class AvailableTimeSlotAdmin(admin.ModelAdmin):
    form = AvailableTimeSlotAdminForm


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