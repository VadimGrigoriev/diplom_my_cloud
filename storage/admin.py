from django.shortcuts import render
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import TabularInline
from django.db.models import Sum, Count
from .models import CustomUser, File


class FileInline(TabularInline):
    model = File
    extra = 0  # Не добавлять дополнительные пустые строки
    fields = ('original_name', 'size', 'uploaded_at', 'last_downloaded', 'comment')
    readonly_fields = ('size', 'uploaded_at', 'last_downloaded')  # Поля только для чтения
    can_delete = True  # Разрешить удаление файлов через инлайн


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    inlines = [FileInline]  # Добавляем инлайн с файлами
    # Поля для отображения в списке
    list_display = ['username', 'email', 'file_count', 'file_size', 'full_name', 'is_staff', 'is_superuser', 'is_active']
    # Поля для фильтрации
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    # Поля для поиска
    search_fields = ('username', 'email', 'full_name')
    # Разделение полей для редактирования
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'full_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Поля для создания пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'password1', 'password2'),
        }),
    )

    def file_count(self, obj):
        return File.objects.filter(user=obj).count()

    file_count.short_description = 'Количество файлов'

    def file_size(self, obj):
        size = File.objects.filter(user=obj).aggregate(Sum('size'))['size__sum'] or 0
        return f"{size} байт"

    file_size.short_description = 'Объём файлов'


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    # Поля для отображения
    list_display = ('original_name', 'user', 'size', 'uploaded_at', 'last_downloaded', 'comment')
    # Поля для фильтрации
    list_filter = ('user', 'uploaded_at', 'last_downloaded')
    # Поля для поиска
    search_fields = ('original_name', 'user__username')
    # Поля для редактирования
    readonly_fields = ('unique_name',)
    actions = ['delete_selected']

    # Добавляем статистику для страницы изменения модели
    change_list_template = "admin/dashboard.html"

    def delete_selected(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Удалено {count} файлов.")

    delete_selected.short_description = "Удалить выбранные файлы"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        total_files = File.objects.count()
        total_size = File.objects.aggregate(Sum('size'))['size__sum'] or 0
        total_users = CustomUser.objects.count()

        extra_context.update({
            'title': "Статистика хранилища",
            'total_files': total_files,
            'total_size': total_size,
            'total_users': total_users,
        })
        return super().changelist_view(request, extra_context=extra_context)
