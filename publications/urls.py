from django.urls import path
from rest_framework.routers import SimpleRouter

from publications.apps import PublicationsConfig
from publications.views import (PostCreateView, PostDeleteView, PostDetailView,
                                PostListView, PostUpdateView, PostViewSet,
                                home)

app_name = PublicationsConfig.name

router = SimpleRouter()
router.register("", PostViewSet)

urlpatterns = [
    path("", home, name="home"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path("detail/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("update/<int:pk>/", PostUpdateView.as_view(), name="post_update"),
    path("delete/<int:pk>/", PostDeleteView.as_view(), name="post_delete"),
    path("list/", PostListView.as_view(), name="post_list"),
] + router.urls
