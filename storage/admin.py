from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, File

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Поля для отображения в списке
    list_display = ['username', 'email', 'full_name', 'is_admin', 'is_staff', 'is_active']
    # Поля для фильтрации
    list_filter = ('is_admin', 'is_staff', 'is_active', 'date_joined')
    # Поля для поиска
    search_fields = ('username', 'email', 'full_name')
    # Разделение полей для редактирования
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'full_name')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Поля для создания пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'password1', 'password2'),
        }),
    )


