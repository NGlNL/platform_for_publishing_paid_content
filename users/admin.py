from django.contrib import admin

from users import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    """Представление администратора для модели User."""

    list_display = (
        "phone",
        "email",
        "tg_nick",
        "is_superuser",
        "id",
        "code",
        "is_active",
        "is_subscribed",
    )
    list_display_links = []
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email",)
    ordering = ("id",)
    readonly_fields = ("id",)
