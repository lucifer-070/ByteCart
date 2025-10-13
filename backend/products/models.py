from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

try:
    # Django 3.1+ has native JSONField
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=64, unique=True)
    attrs = models.JSONField(default=dict, blank=True)  # JSONB-equivalent
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} · {self.sku}"

class Inventory(models.Model):
    # 1:1 with variant (unique FK)
    variant = models.OneToOneField(ProductVariant, on_delete=models.CASCADE, related_name="inventory")
    qty_available = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    def __str__(self):
        return f"{self.variant.sku} · {self.qty_available}"

class Review(models.Model):
    # Associative: User–Product
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()  # 1..5 (validate in serializer/form)
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    STATUS_CHOICES = (
        ("published", "Published"),
        ("hidden", "Hidden"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="published")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "product")]  # one review per user/product
        indexes = [
            models.Index(fields=["product", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.product.name} · {self.user_id} · {self.rating}"
