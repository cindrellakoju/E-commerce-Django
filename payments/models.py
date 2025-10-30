from django.db import models
from users.models import BaseModel
from orders.models import Orders
# Create your models here.

class Payment(BaseModel):
    PAYMENT_STATUS_CHOICES = [
        ('success', 'success'),
        ('failed', 'failed'),
        ('pending', 'pending')
    ]
    order = models.ForeignKey(Orders,on_delete=models.CASCADE,related_name="payment")
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"