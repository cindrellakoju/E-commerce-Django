from django.db import models
from users.models import BaseModel,Users
from products.models import Products
# Create your models here.

class Cart(BaseModel):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="cart")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for {self.user.username}"


class Wishlist(BaseModel):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="wishlists")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="wishlist_items")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product')
        ]


    def __str__(self):
        return f"{self.user.username} wishes for {self.product.name}"
    