from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    """Класс менеджера пользователей"""

    def create_user(self, phone, email, password, **extra_fields):
        if not phone:
            raise ValueError("Укажите телефон")
        user = self.model(phone=phone, email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """Модель пользователя"""

    username = None
    email = models.EmailField(unique=True, verbose_name="Почта")
    phone = models.CharField(max_length=35, verbose_name="Телефон", unique=True)
    tg_nick = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Ник телеграмма"
    )
    avatar = models.ImageField(
        upload_to="users/avatars", blank=True, null=True, verbose_name="Аватар"
    )
    is_subscribed = models.BooleanField(default=False, verbose_name="Подписка")
    code = models.IntegerField(verbose_name="Код подтверждения", blank=True, null=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
