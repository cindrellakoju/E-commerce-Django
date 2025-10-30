from django.db import models
from users.models import BaseModel,Users
from products.models import Products
# Create your models here.
class Orders(BaseModel):
    PAYMENT_METHOD_CHOICES = [
        ('esewa', 'eSewa'),
        ('khalti', 'Khalti'),
        ('paypal', 'PayPal'),
        ('cod', 'Cash on Delivery'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('canceled','Canceled')
    ]

    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
        ('canceled','Canceled')
    ]
    user = models.ForeignKey(Users,on_delete=models.CASCADE,related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2,default=110)
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.order_status}"
    
class OrderItem(BaseModel):
    order = models.ForeignKey(Orders,on_delete=models.CASCADE,related_name='order_items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.product} (x{self.quantity}) in Order {self.order.id}"
