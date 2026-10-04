from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("manage-bank-admin/", admin.site.urls),  # آدرس غیرمعمول برای ادمین
    path("", include("bank.urls")),
]
