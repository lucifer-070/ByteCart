from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from products.models import Category, Product, ProductVariant, Inventory
from orders.models import Cart, CartItem, Order, Payment


class CheckoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.client.force_authenticate(self.user)

        # Basic product + variant + inventory setup
        self.category = Category.objects.create(name="Keyboards", slug="keyboards")
        self.product = Product.objects.create(
            category=self.category,
            name="Alpha 61",
            slug="alpha-61",
            base_price=Decimal("199.99"),
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="ALPHA-61-BLK",
            attrs={"color": "black"},
        )
        self.inventory = Inventory.objects.create(
            variant=self.variant,
            qty_available=10,
        )

    def _create_cart_with_item(self, quantity=2):
        cart, _ = Cart.objects.get_or_create(user=self.user, status="active")
        CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=quantity,
            unit_price=Decimal("199.99"),
        )
        return cart

    def test_checkout_success(self):
        self._create_cart_with_item(quantity=2)

        response = self.client.post(
            "/orders/checkout/",
            {
                "shipping_address": {
                    "recipient_name": "Tester",
                    "line1": "123 Street",
                    "city": "Mumbai",
                    "postal_code": "400001",
                    "country": "IN",
                }
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.content)

        order_id = response.data["id"]
        order = Order.objects.get(id=order_id)

        # order status and total
        self.assertEqual(order.status, "paid")
        self.assertEqual(order.total_amount, Decimal("399.98"))

        # inventory reduced
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.qty_available, 8)

        # cart converted
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.status, "converted")

        # payment created
        payment = Payment.objects.get(order=order)
        self.assertEqual(payment.status, "succeeded")
        self.assertEqual(payment.amount, order.total_amount)

    def test_checkout_fails_when_cart_empty(self):
        # Ensure no active cart or empty cart
        Cart.objects.filter(user=self.user).delete()

        response = self.client.post(
            "/orders/checkout/",
            {"shipping_address": {}},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("No active cart", response.data["detail"])

    def test_checkout_insufficient_stock(self):
        # Request more than available
        self._create_cart_with_item(quantity=20)

        response = self.client.post(
            "/orders/checkout/",
            {"shipping_address": {}},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Insufficient stock", response.data["detail"])

    def test_checkout_idempotency(self):
        self._create_cart_with_item(quantity=2)

        headers = {"HTTP_X_IDEMPOTENCY_KEY": "test-key-123"}

        # First call
        r1 = self.client.post(
            "/orders/checkout/",
            {"shipping_address": {}},
            format="json",
            **headers,
        )
        self.assertEqual(r1.status_code, 201, r1.content)
        first_order_id = r1.data["id"]

        # Second call with same key
        r2 = self.client.post(
            "/orders/checkout/",
            {"shipping_address": {}},
            format="json",
            **headers,
        )
        self.assertIn(r2.status_code, [200, 201])  # we return 200
        second_order_id = r2.data["id"]

        self.assertEqual(first_order_id, second_order_id)

        # Ensure only one order & one payment
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Payment.objects.count(), 1)
