from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser , PermissionsMixin, BaseUserManager, Group, Permission
import random
class Usermanager(BaseUserManager):
    def create_user(self,email,first_name,password=None,**extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active',True)
        
        User = self.model(email=email,first_name=first_name, **extra_fields)
        User.set_password(password)
        User.save(using=self._db)
        return User
    def create_superuser(self,email,first_name,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',True)
        return self.create_user(email,first_name,password,**extra_fields)
    def get_by_natural_key(self, email):
        return self.get(email = email)
        
class user(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    username = models.CharField(_("Username"), max_length=50)
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    num = models.CharField(max_length=12, null=True)
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # def verification_code():
        
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']
    
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True
    )
    
    objects = Usermanager()
    def __str__(self):
        return f"{self.user_id}.{self.email} of {self.username}"
# class verification(models.Model):
#     user = models.models.OneToOneField(user, on_delete=models.CASCADE)
    
# Create your models here.
