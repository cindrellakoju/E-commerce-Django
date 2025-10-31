from django.db import models
from users.models import BaseModel
from orders.models import Orders
# Create your models here.

class Payment(BaseModel):
    # Payment status choices
    PAYMENT_STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending')
    ]

    # Refund workflow status choices
    REFUND_STATUS_CHOICES = [
        ('not_requested', 'Not Requested'),  # default: no refund action yet
        ('requested', 'Requested'),          # refund requested by user/system
        ('approved', 'Approved'),            # refund approved
        ('rejected', 'Rejected'),            # refund rejected
        ('processed', 'Processed')           # refund completed
    ]

    order = models.ForeignKey(
        Orders,
        on_delete=models.CASCADE,
        related_name="payment"
    )
    transaction_id = models.CharField(max_length=100, unique=True)
    pidx = models.CharField(max_length=100, unique=True, null=True, blank=True)

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    refunded = models.BooleanField(default=False)
    refund_status = models.CharField(
        max_length=15,
        choices=REFUND_STATUS_CHOICES,
        default='not_requested'
    )

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.payment_status}"