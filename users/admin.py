from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_expert', 'is_staff', 'is_active']
    list_filter = ['is_expert', 'is_staff', 'is_active']
    search_fields = ['username', 'email']

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные поля', {
            'fields': ('bio', 'position', 'skills', 'avatar', 'is_expert', 'followers'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительные поля', {
            'fields': ('is_expert',),
        }),
    )
