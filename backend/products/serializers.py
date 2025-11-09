from rest_framework import serializers
from .models import Category, Product, ProductVariant, Inventory, Review

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "is_active"]

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ["id", "sku", "attrs", "price_override", "product"]

class InventorySerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)

    class Meta:
        model = Inventory
        fields = ["id", "variant", "qty_available"]

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description", "base_price", "is_active",
            "created_at", "category", "category_id"
        ]
