from django.db import models

class Promotion(models.Model):
    store_name = models.CharField(max_length=255)
    collection_number = models.CharField(max_length=50)
    cup_size = models.CharField(max_length=50)
    discount = models.CharField(max_length=50)
    coupon_name = models.CharField(max_length=255)
    expiration_date = models.DateField(null=True, blank=True)  # อนุญาตให้ NULL ได้

    def __str__(self):
        return self.store_name
