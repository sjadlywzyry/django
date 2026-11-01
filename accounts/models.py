from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        INSTRUCTOR = "instructor", "مدرس"
        STUDENT = "student", "دانشجو"

    email = models.EmailField(
        verbose_name="ایمیل",
        unique=True,
    )

    role = models.CharField(
        verbose_name="نقش",
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    phone = models.CharField(
        verbose_name="شماره تماس",
        max_length=20,
        blank=True,
    )

    email_verified = models.BooleanField(
        verbose_name="ایمیل تأیید شده است",
        default=False,
    )

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.username