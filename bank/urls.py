from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.BankLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("transfer/", views.transfer_start, name="transfer"),
    path("transfer/confirm/", views.transfer_confirm, name="transfer_confirm"),
    path("transactions/", views.transactions, name="transactions"),
    path("receipt/<str:reference>/", views.receipt, name="receipt"),
    path("lang/", views.set_language, name="set_language"),
    path("healthz", views.healthz, name="healthz"),
    path("password/", views.BankPasswordChangeView.as_view(), name="password_change"),
]
