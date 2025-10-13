from django.conf import settings
from django.db import models

class UserProfile(models.Model):
    # Mirrors ERD's User non-auth fields
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    # is_active & created_at are available via auth.User + date_joined
    # Email uniqueness is handled by auth; ensure a unique email in admin/validators if needed.

    def __str__(self):
        return self.full_name or self.user.get_username()

class Address(models.Model):
    # Weak entity: depends on User
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=100, blank=True)
    recipient_name = models.CharField(max_length=255)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=30)
    country = models.CharField(max_length=120, default="IN")
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.recipient_name} · {self.city}"
