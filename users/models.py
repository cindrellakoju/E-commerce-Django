from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
# Create your models here.
class UsersManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)
    
    def get_by_natural_key(self, email):
        """
        Needed for Django's authenticate() function to work
        when USERNAME_FIELD is 'email'.
        """
        return self.get(email=email)
    
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True #prevent django from creating a model for BaseModel

class Users(AbstractBaseUser, PermissionsMixin, BaseModel):
    class UserRoles(models.TextChoices):
        ADMIN = "admin","Admin"
        SELLER = "seller", "Seller"
        CUSTOMER = "customer", "Customer"
    username = models.CharField(unique=True,null=False)
    email = models.EmailField(unique=True,null=False)
    password = models.CharField(null=False)
    fullname = models.CharField(max_length=255, null=False, blank=True, default="")
    address = models.CharField(max_length=500, null=False, blank=True, default="")
    secondary_contact_number=models.CharField(max_length=30,null=False,default="")
    phone = models.CharField(max_length=30,null=False)
    roles = models.CharField(choices=UserRoles.choices,default=UserRoles.CUSTOMER)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UsersManager()  # ← custom manager

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return self.username

