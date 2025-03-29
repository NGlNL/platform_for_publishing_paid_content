import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views import View

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class StripeSessionView(View):
    """Stripe сессия"""

    def post(self, request):
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "rub",
                        "product_data": {
                            "name": "Подписка на платформу",
                        },
                        "unit_amount": 1000 * 100,
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url="http://127.0.0.1:8000/users/success/",
            cancel_url="http://127.0.0.1:8000/",
        )
        return JsonResponse({"session_id": session.id})
