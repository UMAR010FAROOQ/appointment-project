# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, SimpleUserProfile, InstructorProfile
from django.utils.html import format_html

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'profile_image_tag')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'profile_image')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    def profile_image_tag(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />'.format(obj.profile_image.url))
        return '-'
    profile_image_tag.short_description = 'Profile Image'
    profile_image_tag.allow_tags = True

admin.site.register(CustomUser, CustomUserAdmin)

class SimpleUserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(SimpleUserProfile, SimpleUserProfileAdmin)

class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active')

admin.site.register(InstructorProfile, InstructorProfileAdmin)

