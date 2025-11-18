from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from rest_framework import viewsets, permissions, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Cart, CartItem, Order, OrderItem, Payment
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    CheckoutSerializer,
    OrderSerializer,
)
from products.models import Inventory, ProductVariant



class CartView(APIView):
    """
    GET /cart/ -> returns the current user's active cart (creates if missing).
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user, status="active")
        serializer = CartSerializer(cart, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    /cart/items/
    - POST: add item to cart (or increase quantity)
    /cart/items/{id}/
    - PATCH: update quantity
    - DELETE: remove item
    """

    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only items belonging to the current user's carts
        return CartItem.objects.filter(cart__user=self.request.user).select_related(
            "cart", "variant", "variant__product"
        )

class CheckoutView(APIView):
    """
    POST /orders/checkout/
    - Uses the current user's active cart
    - Locks inventory rows
    - Validates stock
    - Creates Order + OrderItems + Payment
    - Marks cart as converted
    """

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user

        # validate request body
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shipping_address = serializer.validated_data.get("shipping_address", {})

        try:
            # lock the cart row
            cart = (
                Cart.objects
                .select_for_update()
                .get(user=user, status="active")
            )
        except Cart.DoesNotExist:
            return Response(
                {"detail": "No active cart found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # load and lock cart items + inventory rows
        items = (
            CartItem.objects
            .select_related("variant", "variant__product")
            .filter(cart=cart)
        )

        if not items.exists():
            return Response(
                {"detail": "Cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        variant_ids = [item.variant_id for item in items]
        inventories_qs = Inventory.objects.select_for_update().filter(
            variant_id__in=variant_ids
        )
        inventories = {inv.variant_id: inv for inv in inventories_qs}

        # validate stock
        for item in items:
            inv = inventories.get(item.variant_id)
            if inv is None:
                return Response(
                    {"detail": f"No inventory record for variant {item.variant_id}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if inv.qty_available < item.quantity:
                return Response(
                    {
                        "detail": f"Insufficient stock for variant {item.variant_id}. "
                                  f"Requested {item.quantity}, available {inv.qty_available}."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # compute total and decrement stock
        total = Decimal("0.00")
        for item in items:
            total += item.unit_price * item.quantity

        for item in items:
            inv = inventories[item.variant_id]
            inv.qty_available -= item.quantity
            inv.save()

        # create order
        order = Order.objects.create(
            user=user,
            status="paid",  # since payment is simulated as instant success
            placed_at=timezone.now(),
            currency="INR",
            total_amount=total,
            shipping_address=shipping_address,
        )

        # create order items snapshot
        bulk_order_items = []
        for item in items:
            bulk_order_items.append(
                OrderItem(
                    order=order,
                    variant=item.variant,
                    product_name=item.variant.product.name,
                    sku=item.variant.sku,
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                    line_total=item.unit_price * item.quantity,
                )
            )
        OrderItem.objects.bulk_create(bulk_order_items)

        # create simulated payment
        Payment.objects.create(
            order=order,
            provider="Simulated",
            amount=total,
            status="succeeded",
            txn_ref=f"SIM-{order.id}-{int(timezone.now().timestamp())}",
            paid_at=timezone.now(),
        )

        # mark cart as converted
        cart.status = "converted"
        cart.save(update_fields=["status"])

        # you might optionally NOT delete cart items to keep history, so we leave them as-is

        # return order details
        out = OrderSerializer(order)
        return Response(out.data, status=status.HTTP_201_CREATED)
