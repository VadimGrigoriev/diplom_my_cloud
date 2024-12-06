from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=150, verbose_name="Полное имя")
    is_admin = models.BooleanField(default=False, verbose_name="Администратор")

    def __str__(self):
        return self.username
