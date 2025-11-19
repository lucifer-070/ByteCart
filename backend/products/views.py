from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q

from .models import Category, Product, ProductVariant, Inventory, Review
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductVariantSerializer,
    InventorySerializer,
    ReviewSerializer,
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

        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        if min_price:
            qs = qs.filter(base_price__gte=min_price)
        if max_price:
            qs = qs.filter(base_price__lte=max_price)

        sort = self.request.query_params.get("sort")
        if sort == "price_asc":
            qs = qs.order_by("base_price")
        elif sort == "price_desc":
            qs = qs.order_by("-base_price")
        elif sort == "name_asc":
            qs = qs.order_by("name")
        elif sort == "name_desc":
            qs = qs.order_by("-name")
        else:
            qs = qs.order_by("-created_at")

        return qs

    @action(detail=True, methods=["get"], permission_classes=[permissions.AllowAny])
    def reviews(self, request, pk=None):
        """
        GET /products/{id}/reviews/ -> list reviews for this product
        """
        reviews = Review.objects.filter(product_id=pk, status="published").order_by("-created_at")
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.select_related("product").order_by("id")
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.AllowAny]


class InventoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Inventory.objects.select_related("variant", "variant__product").order_by("id")
    serializer_class = InventorySerializer
    permission_classes = [permissions.AllowAny]


# -------- NEW: ReviewViewSet --------

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Read for everyone, write only for owners, and staff can do anything.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE methods (GET, HEAD, OPTIONS) always allowed
        if request.method in permissions.SAFE_METHODS:
            return True
        # Staff can edit/delete
        if request.user and request.user.is_staff:
            return True
        # Owners can edit/delete their own
        return obj.user == request.user


class ReviewViewSet(viewsets.ModelViewSet):
    """
    /reviews/ (list the current user's reviews or all for admins)
    /reviews/{id}/ (retrieve/update/delete)
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Review.objects.select_related("product", "user").order_by("-created_at")
        user = self.request.user
        if user.is_staff:
            return qs
        return qs.filter(status="published") | qs.filter(user=user)

    def perform_create(self, serializer):
        # Set the user to the logged-in user
        serializer.save(user=self.request.user)
