from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework.test import APITestCase

from users.forms import PasswordResetForm

User = get_user_model()


class UserCreateViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("users:register")
        self.valid_data = {
            "phone": "81234567890",
            "email": "test@example.com",
            "password1": "123456ay",
            "password2": "123456ay",
        }

    def test_user_creation_success(self):
        """Тест успешного создания пользователя"""
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())
        self.assertEqual(len(mail.outbox), 1)

    def test_user_creation_phone_exists(self):
        """Тест создания пользователя с существующим телефоном"""
        User.objects.create_user(
            phone="81234567890", email="existing@example.com", password="123456ay"
        )
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)
        self.assertEqual(
            form.errors["phone"], ["Пользователь с таким Телефон уже существует."]
        )

    def test_user_creation_invalid_email(self):
        """Тест создания пользователя с неверным адресом электронной почты"""
        self.valid_data["email"] = "invalid-email"
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("email", form.errors)
        self.assertEqual(
            form.errors["email"], ["Введите правильный адрес электронной почты."]
        )


class PasswordResetViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="81234567890", email="test@example.com", password="password123"
        )
        self.url = reverse("users:password_reset")

    def test_password_reset_success(self):
        """Тест успешной отправки кода сброса пароля"""
        response = self.client.post(
            self.url, {"phone": self.user.phone, "email": self.user.email}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("code_sent", response.context)

    def test_invalid_phone(self):
        """Тест отправки кода сброса пароля с неверным телефоном"""
        form_data = {"phone": "123abc", "email": "test@example.com"}
        form = PasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)
