from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from publications.models import Post
from users.models import User


class PostViewSetTests(APITestCase):

    def setUp(self):
        # Создаем пользователя для тестирования
        self.user = User.objects.create_user(
            email="testuser@example.com", phone="81234567890", password="testpass"
        )
        self.client.login(phone="81234567890", password="testpass")

        # Создаем несколько постов для тестирования
        self.post1 = Post.objects.create(
            title="Мир", content="Content of the first post", owner=self.user
        )
        self.post2 = Post.objects.create(
            title="Технология", content="Content of the second post", owner=self.user
        )

    def test_get_posts(self):
        """Тест получения списка постов."""
        url = f'{"http://localhost:8000/publications/"}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post(self):
        """Тест создания нового поста."""
        self.client.login(
            phone="81234567890", password="testpass"
        )  # Аутентификация пользователя
        data = {
            "name": "Новый пост",
            "title": "мир",
            "content": "Содержимое нового поста",
        }
        response = self.client.post(
            reverse("publications:post_create"), data
        )  # Используем метод POST

        self.assertEqual(
            response.status_code, 302
        )  # Проверяем, что произошло перенаправление
        self.assertEqual(Post.objects.count(), 3)  # Проверяем, что пост был создан
        self.assertTrue(Post.objects.filter(title="мир").exists())

    def test_update_post(self):
        """Тест обновления существующего поста."""
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "publications:post_update", kwargs={"pk": self.post1.id}
        )  # Получаем URL для обновления поста
        data = {
            "name": "Новое имя",
            "title": "технология",
            "content": "Updated content of the first post",
        }

        response = self.client.post(url, data)  # Используйте POST для отправки данных
        self.assertEqual(
            response.status_code, status.HTTP_302_FOUND
        )  # Проверяем, что редирект произошел

        self.post1.refresh_from_db()  # Обновляем объект из базы данных
        self.assertEqual(self.post1.title, "технология")

    def test_delete_post(self):
        """Тест удаления поста."""
        self.client.force_authenticate(user=self.user)
        url = f"http://127.0.0.1:8000/publications/delete/{self.post2.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Post.objects.count(), 1)


class HomeViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", phone="1234567890", password="testpass"
        )
        self.client.login(phone="1234567890", password="testpass")

        # Создаем посты для тестирования
        self.post1 = Post.objects.create(
            name="Пост о мире", content="Контент о мире", owner=self.user, title="мир"
        )
        self.post2 = Post.objects.create(
            name="Пост о технологии",
            content="Контент о технологии",
            owner=self.user,
            title="технология",
        )

    def test_home_view(self):
        """Тест главной страницы (home)."""
        response = self.client.get(reverse("publications:home"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Мир")

    def test_no_filter(self):
        """Тест без фильтрации."""
        response = self.client.get(reverse("publications:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пост о мире")
        self.assertContains(response, "Пост о технологии")

    def test_home_view_order(self):
        """Тест сортировки постов по количеству просмотров."""
        self.post1.views_count = 10
        self.post1.save()
        self.post2.views_count = 5
        self.post2.save()

        response = self.client.get(reverse("publications:home"), {"order": "desc"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context["posts"][0], self.post1)
