from django.contrib import admin
from .models import UserProfile, Address

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "phone")

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "label", "recipient_name", "city", "country", "is_default")
    list_filter = ("country", "is_default")
    search_fields = ("recipient_name", "city", "state", "postal_code")
