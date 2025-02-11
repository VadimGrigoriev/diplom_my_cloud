from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.timezone import now
import uuid


class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=350, blank=True, null=True, verbose_name="Полное имя")
    is_admin = models.BooleanField(default=False, verbose_name="Администратор")

    class Meta:
        db_table = 'CustomUser'
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class File(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name="Пользователь"
    )
    original_name = models.CharField(max_length=350, verbose_name="Оригинальное имя файла")
    unique_name = models.CharField(max_length=350, unique=True, verbose_name="Уникальное имя файла")
    size = models.PositiveBigIntegerField(verbose_name="Размер файла (в байтах)")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    last_downloaded = models.DateTimeField(null=True, blank=True, verbose_name="Дата последнего скачивания")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        db_table = 'File'
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

    def __str__(self):
        return self.original_name


class FileToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    file = models.ForeignKey('File', on_delete=models.CASCADE, related_name='tokens')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='file_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'FileToken'
        verbose_name = "Токен файла"
        verbose_name_plural = "Токены файлов"

    def is_valid(self):
        return now() < self.expires_at

    def __str__(self):
        return f"Токен для {self.file.original_name} (истекает в {self.expires_at})"
