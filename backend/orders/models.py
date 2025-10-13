from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator
from django.utils import timezone
from products.models import ProductVariant

try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carts")
    STATUS_CHOICES = (
        ("active", "Active"),
        ("converted", "Converted"),
        ("abandoned", "Abandoned"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Single active cart per user (partial unique index)
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(status="active"),
                name="uniq_active_cart_per_user",
            )
        ]

    def __str__(self):
        return f"{self.user_id} · {self.status}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="cart_items")
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot at time of add

    class Meta:
        indexes = [
            models.Index(fields=["cart"]),
        ]

    def __str__(self):
        return f"{self.cart_id} · {self.variant.sku} · {self.quantity}"

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
        ("failed", "Failed"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    placed_at = models.DateTimeField(default=timezone.now)
    currency = models.CharField(max_length=8, default="INR")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    shipping_address = models.JSONField(default=dict)  # snapshot of address at checkout

    class Meta:
        indexes = [
            models.Index(fields=["user", "-placed_at"]),
        ]

    def __str__(self):
        return f"Order {self.id} · {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="order_items")
    product_name = models.CharField(max_length=200)  # snapshot
    sku = models.CharField(max_length=64)            # snapshot
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.order_id} · {self.sku} · {self.quantity}"

class Payment(models.Model):
    # 1:1 via unique FK to Order
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    provider = models.CharField(max_length=50, default="Simulated")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    STATUS_CHOICES = (
        ("initiated", "Initiated"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="initiated")
    txn_ref = models.CharField(max_length=120, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Payment for Order {self.order_id} · {self.status}"
