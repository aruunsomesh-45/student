from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'academic_tier', 'is_staff')
    list_filter = ('role', 'academic_tier', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('MindConnect Profile', {
            'fields': ('role', 'academic_tier', 'grade_or_year', 'institution', 'department_or_subject', 'avatar_color')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('MindConnect Profile', {
            'fields': ('role', 'academic_tier', 'grade_or_year', 'institution', 'department_or_subject')
        }),
    )
