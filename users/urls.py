from django.contrib.auth.views import LogoutView
from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from users.apps import UsersConfig
from users.services import StripeSessionView
from users.views import (PasswordResetConfirmView, PasswordResetView,
                         SubscribeView, SuccessView, UserCreateAPIView,
                         UserCreateView, UserDetailView, UserUpdateView,
                         confirm_code, login_view, cancel_payment)

app_name = UsersConfig.name

urlpatterns = [
    path("api/register/", UserCreateAPIView.as_view(), name="api_register"),
    path(
        "api_login/",
        TokenObtainPairView.as_view(),
        name="api_login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("login/", login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("confirm/", confirm_code, name="confirm_code"),
    path("profile/<int:pk>/", UserDetailView.as_view(), name="profile"),
    path("profile_update/<int:pk>/", UserUpdateView.as_view(), name="profile_update"),
    path("subscription/", SubscribeView.as_view(), name="subscription"),
    path(
        "create_stripe_session/",
        StripeSessionView.as_view(),
        name="create_stripe_session",
    ),
    path("success/", SuccessView.as_view(), name="success"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "reset_password_confirm/",
        PasswordResetConfirmView.as_view(),
        name="reset_password_confirm",
    ),
    path("cancel/", cancel_payment, name="cancel"),
]
