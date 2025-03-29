from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    """Команда для создания суперпользователя."""

    def handle(self, *args, **options):
        user = User.objects.create(phone="01234567890")
        user.set_password("test")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
