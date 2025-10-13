# backend/products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("ping/", views.ping, name="products-ping"),
]
