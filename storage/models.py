from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=350, verbose_name="Полное имя")
    is_admin = models.BooleanField(default=False, verbose_name="Администратор")

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

    def __str__(self):
        return self.original_name



