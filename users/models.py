from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, verbose_name="Email")
    avatar = models.ImageField(
        upload_to="avatars/", null=True, blank=True, verbose_name="Аватар"
    )
    phone_number = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Номер телефона"
    )
    country = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Страна"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def _str_(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Profile(models.Model):
    CustomUser = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    country = models.CharField(
        max_length=100, verbose_name="Страна", null=True, blank=True
    )
    def __str__(self):
        return f"Профиль {self.CustomUser.username}"
