from django.db import models
from django.contrib.auth.models import User

class Promotion(models.Model):
    # id
    store_name = models.CharField(max_length=255)
    collection_number = models.CharField(max_length=50)
    cup_size = models.CharField(max_length=50)
    discount = models.CharField(max_length=50)
    coupon_name = models.CharField(max_length=255)
    expiration_date = models.DateField(null=True, blank=True)  # อนุญาตให้ NULL ได้

    def __str__(self):
        return self.store_name

class Store(models.Model):
    # id
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10, blank=True, null=True)
    profile_img = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username