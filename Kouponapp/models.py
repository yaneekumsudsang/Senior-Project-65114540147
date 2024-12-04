from django.db import models

class Promotion(models.Model):
    store_name = models.CharField(max_length=255, verbose_name='ชื่อร้าน')
    collection_number = models.CharField(max_length=50, verbose_name='จำนวนสะสม')
    cup_size = models.CharField(max_length=50, verbose_name='ขนาดแก้ว')
    discount = models.CharField(max_length=50, verbose_name='ส่วนลด')
    coupon_name = models.CharField(max_length=255, verbose_name='ชื่อคูปอง')
    expiration_date = models.DateField(null=True, blank=True, verbose_name='วันหมดอายุ')  # อนุญาตให้ NULL ได้

class Meta:
    verbose_name = 'โปรโมชั่น'
    verbose_name_plural = 'โปรโมชั่น'

    def __str__(self):
        return self.store_name
