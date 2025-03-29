from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django.forms import ModelForm

from publications.forms import StyleFormMixin
from users.models import User


class UserRegisterForm(UserCreationForm):
    """Форма регистрации пользователя"""

    phone = forms.CharField(max_length=35)
    email = forms.EmailField()
    password1 = forms.CharField(label="password1", widget=forms.PasswordInput)
    password2 = forms.CharField(label="password2", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("phone", "email", "password1", "password2")

    def clean_phone(self):
        """Валидация номера телефона."""
        phone = self.cleaned_data.get("phone")
        if phone and not phone.isdigit():
            raise forms.ValidationError("Номер телефона должен содержать только цифры.")
        if phone and len(phone) != 11:
            raise forms.ValidationError("Номер телефона должен содержать 11 цифр.")
        if phone and phone[0] != "8":
            raise forms.ValidationError("Номер телефона должен начинаться с цифры 8.")
        return phone

    def clean_email(self):
        """Валидация почты."""
        email = self.cleaned_data.get("email")
        if "@" not in email:
            raise forms.ValidationError("Email должен содержать символ '@'.")
        return email


class PasswordResetForm(StyleFormMixin, forms.Form):
    """Форма для сброса пароля"""

    phone = forms.CharField(max_length=35)
    email = forms.EmailField()

    def clean_phone(self):
        """Валидация номера телефона."""
        phone = self.cleaned_data.get("phone")
        if not phone.isdigit():
            raise forms.ValidationError("Номер телефона должен содержать только цифры.")
        return phone


class LoginForm(forms.Form):
    """Форма авторизации"""

    phone = forms.CharField(max_length=35)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        """Валидация формы"""
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone")
        password = cleaned_data.get("password")

        if phone and password:
            user = authenticate(username=phone, password=password)
            if not user:
                raise forms.ValidationError("Неверный логин или пароль")
            if not user.is_active:
                raise forms.ValidationError("Аккаунт не активен")

        return cleaned_data


class ProfileForm(StyleFormMixin, ModelForm):
    """Форма профиля пользователя"""

    class Meta:
        model = User
        fields = ("avatar", "tg_nick", "email", "phone")


class CustomSetPasswordForm(StyleFormMixin, SetPasswordForm):
    """Форма смены пароля"""

    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        required=True,
        help_text="Пароль должен содержать как минимум 8 символов.",
    )
    new_password2 = forms.CharField(
        label="Подтверждение пароля",
        strip=False,
        required=True,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Подтверждение пароля.",
    )
