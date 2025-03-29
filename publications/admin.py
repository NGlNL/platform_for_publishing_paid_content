from django.contrib import admin

from publications.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "content", "date_posted", "views_count", "owner")
    list_filter = ("id",)
    search_fields = ("name", "date_posted")
