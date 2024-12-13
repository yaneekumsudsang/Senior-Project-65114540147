from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, Permission

class Store(models.Model):
        # id
    store_name = models.CharField(max_length=255, unique=True, verbose_name="ชื่อร้าน")
    owner = models.ForeignKey('Kouponapp.Owner', on_delete=models.CASCADE, related_name='stores',verbose_name="เจ้าของร้าน")
    class Meta:
        verbose_name_plural = 'ร้าน'
        verbose_name = 'ร้าน'

    def __str__(self):
        return self.store_name
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, verbose_name="ชื่อผู้ใช้")
    phone = models.CharField(max_length=10, blank=True, null=True, verbose_name="เบอร์โทรศัพท์")
    profile_img = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="รูปโปรไฟล์")

    class Meta:
        verbose_name_plural = 'สมาชิก'
        verbose_name = 'สมาชิก'

    def __str__(self):
        return self.user.username

class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile', verbose_name="ชื่อผู้ใช้")
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name="เบอร์โทรศัพท์")
    shop_logo = models.ImageField(upload_to='shop_logos/', null=True, blank=True, verbose_name="โลโก้ร้าน") # อนุญาตให้ว่างได้

    class Meta:
        verbose_name_plural = 'เจ้าของร้าน'
        verbose_name = 'เจ้าของร้าน'

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Promotion(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='promotions', verbose_name="ชื่อร้าน")
    picture = models.ImageField(upload_to='promotions/', null=True, blank=True, verbose_name="รูปโปรโมชั่น")
    cupsize = models.CharField(max_length=50, null=True, blank=True, verbose_name="ขนาดแก้ว")
    cups = models.IntegerField(null=True, blank=True,verbose_name="จำนวนแก้วที่สะสม")
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="ส่วนลด")
    free = models.IntegerField(null=True, blank=True, verbose_name="จำนวนแก้วที่ฟรี")
    name = models.CharField(max_length=255, verbose_name="ชื่อโปรโมชั่น")
    start = models.DateField(verbose_name="วันที่เริ่มใช้งานคูปอง")
    end = models.DateField(verbose_name="วันหมดอายุคูปอง")

    class Meta:
        verbose_name_plural = 'โปรโมชั่น'
        verbose_name = 'โปรโมชั่น'

    def __str__(self):
        return f"{self.name} ({self.store.name})"

class Coupon(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ไอดีคูปอง")
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, verbose_name="ไอดีโปรโมชั่น")
    used = models.BooleanField(default=False, verbose_name="ตรวจสอบการใช้งาน")
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="สมาชิกที่ใช้งานคูปอง")

    class Meta:
        verbose_name_plural = 'คูปอง'
        verbose_name = 'คูปอง'

    def __str__(self):
        return f"Coupon {self.id}"
