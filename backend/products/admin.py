from django.contrib import admin
from .models import Category, Product, ProductVariant, Inventory, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "parent", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "base_price", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(ProductVariant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "sku")
    search_fields = ("sku", "product__name")

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("id", "variant", "qty_available")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "rating", "status", "created_at")
    list_filter = ("status", "rating")
    search_fields = ("product__name", "user__username", "title", "body")
