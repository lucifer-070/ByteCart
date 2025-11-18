from decimal import Decimal
from rest_framework import serializers
from products.models import ProductVariant
from products.serializers import ProductVariantSerializer
from .models import Cart, CartItem, Order, OrderItem, Payment


class CartItemSerializer(serializers.ModelSerializer):
    variant_detail = ProductVariantSerializer(source="variant", read_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "variant",
            "variant_detail",
            "quantity",
            "unit_price",
            "subtotal",
        ]
        extra_kwargs = {
            # variant and quantity will be provided by client
            "unit_price": {"read_only": True},
        }

    def get_subtotal(self, obj):
        return obj.unit_price * obj.quantity

    def _get_or_create_active_cart(self, user):
        # Will respect the "single active cart per user" constraint
        cart, _ = Cart.objects.get_or_create(user=user, status="active")
        return cart

    def _compute_unit_price(self, variant: ProductVariant) -> Decimal:
        if variant.price_override is not None:
            return variant.price_override
        return variant.product.base_price

    def create(self, validated_data):
        """
        Create or update a CartItem for the current user's active cart.
        If the same variant already exists in the cart, we just bump quantity.
        """
        request = self.context["request"]
        user = request.user

        cart = self._get_or_create_active_cart(user)
        variant = validated_data["variant"]
        quantity = validated_data["quantity"]

        unit_price = self._compute_unit_price(variant)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={"quantity": quantity, "unit_price": unit_price},
        )

        if not created:
            item.quantity += quantity
            # unit_price stays as original snapshot
            item.save()

        return item

    def update(self, instance, validated_data):
        """
        Update quantity only. If quantity <= 0, delete the item.
        """
        quantity = validated_data.get("quantity", instance.quantity)

        if quantity <= 0:
            instance.delete()
            # Represent deletion to caller; you could also raise a validation error instead.
            return instance

        instance.quantity = quantity
        instance.save()
        return instance


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "status",
            "created_at",
            "updated_at",
            "items",
            "total_amount",
        ]

    def get_total_amount(self, obj):
        total = Decimal("0.00")
        for item in obj.items.all():
            total += item.unit_price * item.quantity
        return total

# ---------- NEW: ORDER + PAYMENT SERIALIZERS ----------

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "variant",
            "product_name",
            "sku",
            "unit_price",
            "quantity",
            "line_total",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "provider",
            "amount",
            "status",
            "txn_ref",
            "paid_at",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "placed_at",
            "currency",
            "total_amount",
            "shipping_address",
            "items",
            "payment",
        ]
        read_only_fields = ["user", "status", "placed_at", "total_amount"]


class CheckoutSerializer(serializers.Serializer):
    """
    Input for /orders/checkout/ endpoint.
    You can expand this later (e.g., address_id, notes, etc.).
    """
    shipping_address = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        required=False,
    )