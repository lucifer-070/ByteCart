from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ProductVariantViewSet,
    InventoryViewSet,
    ReviewViewSet,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"variants", ProductVariantViewSet, basename="variant")
router.register(r"inventory", InventoryViewSet, basename="inventory")
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),
]
