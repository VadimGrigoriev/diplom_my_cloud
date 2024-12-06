from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('full_name', 'is_admin')}),
    )
    list_display = ['username', 'email', 'full_name', 'is_admin', 'is_staff']
    search_fields = ['username', 'email', 'full_name']
