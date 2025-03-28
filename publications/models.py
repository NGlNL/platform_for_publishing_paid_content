from django.db import models

from users.models import User

TITLE_CHOICES = (
    ("мир", "Мир"),
    ("страны", "Страны"),
    ("технология", "Технология"),
    ("одежда", "Одежда"),
    ("культура", "Культура"),
    ("бизнес", "Бизнес"),
    ("политика", "Политика"),
    ("мнение", "Мнение"),
    ("наука", "Наука"),
    ("здоровье", "Здоровье"),
    ("стиль", "Стиль"),
    ("путешествие", "Путешествие"),
    ("другое", "Другое"),
)


class Post(models.Model):
    name = models.CharField(max_length=100, verbose_name="Заголовок записи")
    content = models.TextField(verbose_name="Текст записи")
    image = models.ImageField(
        upload_to="media/images/", blank=True, null=True, verbose_name="Изображение"
    )
    date_posted = models.DateTimeField(auto_now_add=True)
    views_count = models.PositiveIntegerField(
        default=0, verbose_name="Счётчик просмотров"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(
        max_length=100,
        choices=TITLE_CHOICES,
        verbose_name="Категория",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        ordering = ["-date_posted", "views_count"]

    def __str__(self):
        return self.name

    @classmethod
    def get_most_viewed(cls):
        return cls.objects.order_by("-views_count").first()
