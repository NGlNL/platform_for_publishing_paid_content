from rest_framework import serializers

from publications.models import Post


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Post"""

    class Meta:
        model = Post
        fields = "__all__"
