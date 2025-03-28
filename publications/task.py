from celery import shared_task
from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER


@shared_task
def send_delete_mail(user_email, post_name):
    """Отправка уведомления об удалении записи"""
    send_mail(
        subject="Запись удалена",
        message=f"Ваша запись '{post_name}' была удалена.",
        from_email=EMAIL_HOST_USER,
        recipient_list=[user_email],
    )
