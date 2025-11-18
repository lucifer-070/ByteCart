from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartView, CartItemViewSet, CheckoutView

router = DefaultRouter()
router.register(r"cart/items", CartItemViewSet, basename="cart-items")

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart-detail"),
    path("orders/checkout/", CheckoutView.as_view(), name="orders-checkout"),
    path("", include(router.urls)),
]
