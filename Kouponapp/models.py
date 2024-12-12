from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, Permission

class Store(models.Model):
    # id
    store_name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey('Kouponapp.Owner', on_delete=models.CASCADE, related_name='stores')

    def __str__(self):
        return self.store_name
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    profile_img = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
    phone = models.CharField(max_length=15, null=True, blank=True)
    shop_logo = models.ImageField(upload_to='shop_logos/', null=True, blank=True) # อนุญาตให้ว่างได้

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Promotion(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='promotions')
    picture = models.ImageField(upload_to='promotions/', null=True, blank=True)
    cupsize = models.CharField(max_length=50, null=True, blank=True)
    cups = models.IntegerField(null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    free = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.store.name})"

class Coupon(models.Model):
    id = models.AutoField(primary_key=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)

    def __str__(self):
        return f"Coupon {self.id}"
