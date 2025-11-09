from rest_framework import viewsets, permissions, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


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
