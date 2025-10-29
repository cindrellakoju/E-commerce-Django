from django.db import models
from users.models import BaseModel,Users
from django.utils.text import slugify
from django.core.validators import MinValueValidator,MaxValueValidator
# Create your models here.
class ProductCategory(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,blank=True)
    parent_id = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subcategories'
    )

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args,**kwargs)

    def __str__(self):
        return self.name
    
class Products(BaseModel):
    seller= models.ForeignKey(Users, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductImage(BaseModel):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} Image"

class ProductReview(BaseModel):
    reviewer = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="reviews")
    review_msg = models.CharField(max_length=500, null=True, blank=True)
    review_star = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],null=True,blank=True
    )

    def __str__(self):
        return f"{self.review_star} star by {self.reviewer} on {self.product.name}"