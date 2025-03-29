from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (Http404, HttpResponseForbidden, HttpResponseNotFound,
                         HttpResponseRedirect)
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from rest_framework import viewsets
from rest_framework.reverse import reverse

from publications.forms import PostForm
from publications.models import TITLE_CHOICES, Post
from publications.serializers import PostSerializer

from .task import send_delete_mail


class PostViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Post"""

    queryset = Post.objects.all()
    serializer_class = PostSerializer


def home(request):
    """View для главной страницы"""
    title_filter = request.GET.get("title")
    order = request.GET.get("order")
    most_viewed_post = Post.get_most_viewed()
    user = request.user
    posts = Post.objects.all()

    if user.is_authenticated:
        if user.is_subscribed:
            posts = posts
        else:
            posts = posts.filter(owner__is_subscribed=False)
    else:
        posts = posts.filter(owner__is_subscribed=False)
    if title_filter:
        posts = posts.filter(title__icontains=title_filter)
    if order == "desc":
        posts = posts.order_by("-views_count")
    elif order == "asc":
        posts = posts.order_by("views_count")
    for post in posts:
        if post.title is None:
            post.title_display = "Без категории"
        else:
            post.title_display = post.title
    title_choices = TITLE_CHOICES
    return render(
        request,
        "publications/home.html",
        {
            "posts": posts,
            "title_choices": title_choices,
            "most_viewed_post": most_viewed_post,
        },
    )


class PostCreateView(CreateView, LoginRequiredMixin):
    """'Представление для создания записи."""

    model = Post
    form_class = PostForm
    template_name = "publications/post_create.html"
    success_url = reverse_lazy("publications:home")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class PostUpdateView(
    UpdateView,
):
    """'Представление для обновления записи."""

    model = Post
    form_class = PostForm
    template_name = "publications/post_update.html"

    def get_success_url(self):
        return reverse_lazy("publications:post_detail", kwargs={"pk": self.object.pk})


class PostDeleteView(DeleteView):
    """Представление для удаления записи."""

    model = Post
    template_name = "publications/post_confirm_delete.html"
    success_url = reverse_lazy("publications:home")

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            return HttpResponseNotFound("Пост не найден.")
        if self.object.owner != request.user:
            return HttpResponseForbidden("Вы не можете удалить этот пост.")
        send_delete_mail.delay(self.object.owner.email, self.object.name)
        self.object.delete()
        return HttpResponseRedirect(reverse("publications:home"))


class PostDetailView(
    DetailView,
):
    """'Представление для сообщения."""

    model = Post
    template_name = "publications/post_detail.html"
    context_object_name = "post"

    def get(self, request, *args, **kwargs):
        """Метод для увеличения количества просмотров сообщения."""
        response = super().get(request, *args, **kwargs)
        self.object.views_count += 1
        self.object.save()
        return response


class PostListView(ListView):
    """'Представление для списка сообщений."""

    model = Post
    template_name = "publications/post_list.html"
    context_object_name = "posts"
