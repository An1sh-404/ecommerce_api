from django.db import models
from django.conf import settings
from django.utils import timezone
# Create your models here.


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    AUTHORIZED = "authorized", "Authorized"
    PAID = "paid", "Paid"
    ALLOCATED = "allocated", "Allocated"
    SHIPPED = "shipped", "Shipped"
    COMPLETED = "completed", "Completed"
    CANCELED = "canceled", "Canceled"
    REFUNDED = "refunded", "Refunded"


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name = "orders"
    )
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    order_number = models.CharField(max_length=32, unique=True)
    currency = models.CharField(max_length=3, default="USD")

    subtotal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)

    shipping_name = models.CharField(max_length=200)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_postcode = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=2)

    billing_name = models.CharField(max_length=200)
    billing_address1 = models.CharField(max_length=255)
    billing_address2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postcode = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=2)

    # Payment intent references
    payment_provider = models.CharField(max_length=50, blank=True)
    payment_intent_id = models.CharField(max_length=128, blank=True, db_index=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["status"]),
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.PositiveIntegerField()
    product_sku = models.CharField(max_length=64)
    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    attributes_json = models.JSONField(default=dict, blank=True)

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    provider = models.CharField(max_length=50)
    intent_id = models.CharField(max_length=128, db_index=True)
    status = models.CharField(max_length=32, default="requires_confirmation")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    raw_response = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class PaymentTransaction(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=32)  # e.g., 'authorization', 'capture', 'refund'
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    provider_status = models.CharField(max_length=64)
    provider_code = models.CharField(max_length=64, blank=True)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)