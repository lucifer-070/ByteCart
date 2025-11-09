from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Category, Product, ProductVariant, Inventory
from .serializers import (
    CategorySerializer, ProductSerializer,
    ProductVariantSerializer, InventorySerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Product.objects.select_related("category").order_by("-created_at")
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category_id=category)
        return qs

    @action(detail=True, methods=["get"], permission_classes=[permissions.AllowAny])
    def variants(self, request, pk=None):
        variants = ProductVariant.objects.filter(product_id=pk).order_by("id")
        return Response(ProductVariantSerializer(variants, many=True).data)

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.select_related("product").order_by("id")
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.AllowAny]

class InventoryViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    """Read-only inventory exposure"""
    queryset = Inventory.objects.select_related("variant", "variant__product").order_by("id")
    serializer_class = InventorySerializer
    permission_classes = [permissions.AllowAny]
