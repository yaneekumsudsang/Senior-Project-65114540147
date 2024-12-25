from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, Permission
from django.core.validators import MinValueValidator, MaxValueValidator

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, verbose_name="ชื่อผู้ใช้")
    is_owner = models.BooleanField(default=False, verbose_name="เป็นเจ้าของร้าน")  # ใช้ BooleanField แทนค่า 1/0
    phone = models.CharField(max_length=10, blank=True, null=True, verbose_name="เบอร์โทรศัพท์")
    profile_img = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="รูปโปรไฟล์")
    shop_logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True, verbose_name="โลโก้ร้าน")

    class Meta:
        verbose_name_plural = 'สมาชิก'
        verbose_name = 'สมาชิก'

    def __str__(self):
        return self.user.username

class Store(models.Model):
    id = models.AutoField(primary_key=True)  # ID ของร้านค้า
    store_name = models.CharField(max_length=255, verbose_name="ชื่อร้าน")  # ชื่อร้านค้า
    owner = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='stores',
        verbose_name="เจ้าของร้าน"
    )  # เชื่อมกับ Member (ผู้เป็นเจ้าของร้าน)

    class Meta:
        verbose_name = "ร้านค้า"
        verbose_name_plural = "ร้านค้าทั้งหมด"

    def __str__(self):
        return self.store_name

class Promotion(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='promotions', verbose_name="ชื่อร้าน")
    picture = models.ImageField(upload_to='promotions/', null=True, blank=True, verbose_name="รูปโปรโมชั่น")
    cupsize = models.CharField(max_length=50, null=True, blank=True, verbose_name="ขนาดแก้ว")
    cups = models.PositiveIntegerField(null=True, blank=True,verbose_name="จำนวนแก้วที่สะสม")
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="ส่วนลด",
    validators=[
        MinValueValidator(0),  # ส่วนลดขั้นต่ำ 0%
        MaxValueValidator(100)  # ส่วนลดสูงสุด 100%
    ])
    free = models.PositiveIntegerField(null=True, blank=True, verbose_name="จำนวนแก้วที่ฟรี")
    name = models.CharField(max_length=100, verbose_name="ชื่อโปรโมชั่น")
    details = models.CharField(max_length=200, null=True, blank=True, verbose_name="รายละเอียดโปรโมชั่น")
    start = models.DateField(verbose_name="วันที่เริ่มใช้งานคูปอง")
    end = models.DateField(verbose_name="วันหมดอายุคูปอง")

    class Meta:
        verbose_name_plural = 'โปรโมชั่น'
        verbose_name = 'โปรโมชั่น'

    def __str__(self):
        return f"{self.name} ({self.store.store_name})"

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
