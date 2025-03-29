import random
import smtplib

from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (CreateView, DetailView, TemplateView,
                                  UpdateView)
from rest_framework.generics import CreateAPIView, get_object_or_404

from config import settings
from config.settings import EMAIL_HOST_USER
from publications.models import Post
from users.forms import (LoginForm, PasswordResetForm, ProfileForm,
                         UserRegisterForm)
from users.models import User
from users.serializers import UserSerializer


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class UserCreateView(CreateView):
    """Создание нового пользователя и отправка кода подтверждения на почту"""

    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"

    def form_valid(self, form):
        """Валидация формы регистрации пользователя и отправка кода подтверждения на почту"""
        if User.objects.filter(phone=form.cleaned_data.get("phone")).exists():
            form.add_error("phone", "Такой номер телефона уже зарегистрирован")
            return self.form_invalid(form)
        if User.objects.filter(email=form.cleaned_data.get("email")).exists():
            form.add_error("email", "Пользователь с такой почтой уже зарегистрирован")
            return self.form_invalid(form)
        try:
            validate_email(form.cleaned_data.get("email"))
        except ValidationError:
            form.add_error("email", "Адрес электронной почты недействителен")
            return self.form_invalid(form)

        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get("password1"))
        user.is_active = False
        code = random.randint(0000, 9999)
        user.code = code
        user.save()
        self.request.session["phone"] = user.phone
        try:
            send_mail(
                subject="Подтверждение регистрации",
                message=f"Ваш код подтверждения: {code}",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
            )
        except smtplib.SMTPRecipientsRefused:
            form.add_error("email", "Почтовый адрес не существует")
            return self.form_invalid(form)

        return redirect("users:confirm_code")


def confirm_code(request):
    """Проверка кода подтверждения регистрации"""
    phone = request.session.get("phone")
    user = get_object_or_404(User, phone=phone)

    if request.method == "POST":
        user_code = request.POST.get("code")
        if user_code == str(user.code):
            user.is_active = True
            user.code = None
            user.save()
            return redirect("users:login")
        else:
            return render(
                request,
                "users/confirm_code.html",
                {"error": "Неверный код подтверждения"},
            )

    return render(request, "users/confirm_code.html")


def login_view(request):
    """Вход пользователя"""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get("phone")
            password = form.cleaned_data.get("password")
            user = authenticate(username=phone, password=password)
            if user is not None:
                login(request, user)
                return redirect("publications:home")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


class PasswordResetView(View):
    """Отправка кода на почту и сброс пароля пользователя"""

    def get(self, request):
        form = PasswordResetForm()
        return render(request, "users/password_reset.html", {"form": form})

    def post(self, request):
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            phone = form.cleaned_data.get("phone")
            email = form.cleaned_data.get("email")

            try:
                user = User.objects.get(phone=phone, email=email)
            except User.DoesNotExist:
                form.add_error(
                    "phone",
                    "Пользователь с таким номером телефона и электронной почтой не найден.",
                )
                return self.form_invalid(form)

            code = random.randint(1000, 9999)
            user.code = code
            user.save()

            send_mail(
                subject="Код сброса пароля",
                message=f"Ваш код для сброса пароля: {code}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
            )

            request.session["phone"] = user.phone
            request.session["code"] = code

            return render(
                request, "users/password_reset.html", {"form": form, "code_sent": True}
            )

        entered_code = request.POST.get("code")
        if entered_code and str(entered_code) == str(request.session.get("code")):
            del request.session["phone"]
            del request.session["code"]
            return redirect("users:reset_password_confirm")
        else:
            if entered_code:
                form.add_error("code", "Неверный код. Пожалуйста, попробуйте еще раз.")

        return self.form_invalid(form)

    def form_invalid(self, form):
        return render(self.request, "users/password_reset.html", {"form": form})


class PasswordResetConfirmView(View):
    """Сброс пароля пользователя"""

    def get(self, request, phone=None):
        if not phone:
            return render(request, "users/reset_password_confirm.html", {"phone": None})

        try:
            user = User.objects.get(profile__phone=phone)
        except User.DoesNotExist:
            return HttpResponseBadRequest(
                "Пользователь с данным номером телефона не найден"
            )

        form = SetPasswordForm(user=user)
        return render(
            request, "users/reset_password_confirm.html", {"form": form, "phone": phone}
        )

    def post(self, request):
        phone = request.POST.get("phone")
        password1 = request.POST.get("new_password1")
        password2 = request.POST.get("new_password2")
        if not phone or not password1 or not password2:
            return HttpResponseBadRequest(
                "Номер телефона и новый пароль должны быть указаны"
            )

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return HttpResponseBadRequest(
                "Пользователь с данным номером телефона не найден"
            )
        form = SetPasswordForm(user=user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:login")

        return render(
            request, "users/reset_password_confirm.html", {"form": form, "phone": phone}
        )


class UserDetailView(DetailView):
    """Просмотр профиля пользователя"""

    model = User
    template_name = "users/profile.html"
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        posts = Post.objects.filter(owner=user)
        context["posts"] = posts
        return context


class UserUpdateView(UpdateView):
    """Обновление профиля пользователя"""

    model = User
    form_class = ProfileForm
    template_name = "users/profile_update.html"

    def get_success_url(self):
        return reverse_lazy("users:profile", kwargs={"pk": self.object.pk})


class SubscribeView(TemplateView):
    """Подписка пользователя"""

    template_name = "users/subscription.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stripe_public_key = settings.STRIPE_TEST_PUBLISHABLE_KEY
        context["stripe_public_key"] = stripe_public_key
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())


class SuccessView(TemplateView):
    """Успешная оплата подписки"""

    template_name = "users/success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            user.is_subscribed = True
            user.save()
            context['message'] = "Подписка успешно оформлена!"
        else:
            return redirect('login')
        return context
