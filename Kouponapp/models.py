import io

from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, Permission
from django.core.validators import MinValueValidator, MaxValueValidator
import segno
import os
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from decimal import Decimal
import random
import string

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, verbose_name="ชื่อผู้ใช้")
    is_owner = models.BooleanField(default=False, verbose_name="เป็นเจ้าของร้าน")
    phone = models.CharField(max_length=10, blank=True, null=True, verbose_name="เบอร์โทรศัพท์")
    profile_img = models.ImageField(upload_to='profiles/', blank=True, null=True, max_length=255, verbose_name="รูปโปรไฟล์")
    card_number = models.CharField(max_length=16, unique=True, null=True, blank=True, verbose_name="เลขบัตร")

    class Meta:
        verbose_name_plural = 'สมาชิก'
        verbose_name = 'สมาชิก'

    def __str__(self):
        return self.user.username

    def ensure_wallet_exists(self):
        """
        ตรวจสอบและสร้าง wallet ถ้ายังไม่มี
        """
        if not hasattr(self, 'wallet'):
            return Wallet.objects.create(member=self)
        return self.wallet

    def generate_card_number(self):
        """สร้างเลขบัตรแบบสุ่ม 10 หลัก"""
        while True:
            # สร้างเลขบัตร 10 หลัก
            card_number = ''.join(random.choices(string.digits, k=10))

            # ตรวจสอบว่าเลขบัตรซ้ำหรือไม่
            if not Member.objects.filter(card_number=card_number).exists():
                return card_number

    def save(self, *args, **kwargs):
        # ถ้ายังไม่มีเลขบัตร ให้สร้างใหม่
        if not self.card_number:
            self.card_number = self.generate_card_number()
        super().save(*args, **kwargs)

def save(self, *args, **kwargs):
    # ถ้ายังไม่มีเลขบัตร ให้สร้างใหม่
    if not self.card_number:
        self.card_number = self.generate_card_number()
    super().save(*args, **kwargs)

class Store(models.Model):
    id = models.AutoField(primary_key=True)  # ID ของร้านค้า
    store_name = models.CharField(max_length=255, verbose_name="ชื่อร้าน")  # ชื่อร้านค้า
    owner = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        related_name='store',
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
    details = models.TextField(max_length=200, null=True, blank=True, verbose_name="รายละเอียดโปรโมชั่น")
    start = models.DateField(verbose_name="วันที่เริ่มใช้งานคูปอง")
    end = models.DateField(verbose_name="วันหมดอายุคูปอง")
    count = models.PositiveIntegerField(default=1, verbose_name="จำนวนคูปอง")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        default=0,
        verbose_name="ราคาสินค้า"
    )

    class Meta:
        verbose_name_plural = 'โปรโมชั่น'
        verbose_name = 'โปรโมชั่น'

    #def __init__(self, *args, **kwargs):
    #    super().__init__(args, kwargs)
    #    self.coupon_set = None

    def __str__(self):
        return f"{self.name} ({self.store.store_name})"

class Coupon(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ไอดีคูปอง")
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='coupons', verbose_name="ไอดีโปรโมชั่น")
    promotion_count = models.PositiveIntegerField(verbose_name="ลำดับคูปอง", default=0)
    collect = models.BooleanField(default=False, verbose_name="ตรวจสอบการสะสม")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True, verbose_name="สมาชิกที่สะสมคูปอง")
    collect_qr_code_url = models.URLField(max_length=200, blank=True, null=True, verbose_name="URL ของ QR Code สำหรับเก็บคูปอง")
    use_qr_code_url = models.URLField(max_length=200, blank=True, null=True, verbose_name="URL ของ QR Code สำหรับใช้คูปอง")
    collect_qr_code_image = models.ImageField(upload_to='collect_qr_codes/', blank=True, null=True, verbose_name="ภาพ QR Code สำหรัลสะสมคูปอง")
    use_qr_code_url_image = models.ImageField(upload_to='use_qr_codes/', blank=True, null=True, verbose_name="ภาพ QR Code สำหรับใช้คูปอง")
    collected_at = models.DateTimeField(null=True, blank=True, verbose_name="เวลาที่สะสม")
    used = models.BooleanField(default=False, verbose_name="ตรวจสอบการใช้งาน")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="เวลาที่ใช้งาน")

    class Meta:
        verbose_name_plural = 'คูปอง'
        verbose_name = 'คูปอง'

    def __str__(self):
        return f"Coupon {self.id} for Promotion {self.promotion.id}"

    def generate_qr_code(self):
        if not self.collect_qr_code_url:
            return

        # Create QR code
        qr = segno.make(self.collect_qr_code_url)

        # Save to static directory
        static_qr_path = os.path.join(settings.BASE_DIR, 'static', 'qr_codes')
        os.makedirs(static_qr_path, exist_ok=True)
        static_file_path = os.path.join(static_qr_path, f'qr_code_{self.promotion.id}_{self.id}.png')
        qr.save(static_file_path, scale=10)

        # Save to media directory for database field
        buffer = io.BytesIO()
        qr.save(buffer, kind='png', scale=10)
        buffer.seek(0)

        # Generate filename for the database
        filename = f'qr_code_{self.promotion.id}_{self.id}.png'

        # Save to database field if not already set
        if not self.collect_qr_code_image:
            self.collect_qr_code_image.save(filename, ContentFile(buffer.getvalue()), save=False)

        buffer.close()

    def save(self, *args, **kwargs):
        # First save to get the ID if it's a new instance
        super().save(*args, **kwargs)

        # Generate QR code if URL is set but image isn't generated yet
        if self.collect_qr_code_url and (not self.collect_qr_code_image or not os.path.exists(self.collect_qr_code_image.path)):
            self.generate_qr_code()
            # Save again to update the image field
            super().save(update_fields=['collect_qr_code_image'] if self.id else None)

class ScannedQRCode(models.Model):
    scanned_text = models.TextField()  # ข้อมูลที่ได้จากการสแกน
    timestamp = models.DateTimeField(auto_now_add=True)  # เวลาที่สแกน
    is_url = models.BooleanField(default=False)  # ตรวจสอบว่าเป็น URL หรือไม่

    def __str__(self):
        return f"{self.scanned_text} - {self.timestamp}"

class StoreOwnerRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="ชื่อร้าน")
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'รอการอนุมัติ'),
            ('approved', 'อนุมัติแล้ว'),
            ('rejected', 'ปฏิเสธ')
        ],
        default='pending'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_requests'
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_store_owner_request')
        ]

class Wallet(models.Model):
    member = models.OneToOneField(
        'Member',
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name="เจ้าของกระเป๋าเงิน"
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="ยอดเงินคงเหลือ"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่สร้าง")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="อัพเดทล่าสุด")

    class Meta:
        verbose_name = "กระเป๋าเงิน"
        verbose_name_plural = "กระเป๋าเงินทั้งหมด"

    def __str__(self):
        return f"กระเป๋าเงินของ {self.member.user.first_name}"

    def deduct_balance(self, amount):
        """
        หักเงินจากกระเป๋าเงิน
        """
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

    def add_balance(self, amount):
        """
        เพิ่มเงินในกระเป๋าเงิน
        """
        self.balance += amount
        self.save()
        return True

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEBIT', 'จ่ายเงิน'),
        ('CREDIT', 'รับเงิน'),
    ]

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="กระเป๋าเงิน"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="จำนวนเงิน"
    )
    transaction_type = models.CharField(
        max_length=6,
        choices=TRANSACTION_TYPES,
        verbose_name="ประเภทธุรกรรม"
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="รายละเอียด"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="วันที่ทำรายการ"
    )

    class Meta:
        verbose_name = "ประวัติธุรกรรม"
        verbose_name_plural = "ประวัติธุรกรรมทั้งหมด"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - ฿{self.amount}"

@receiver(post_save, sender=Member)
def create_wallet(sender, instance, created, **kwargs):
    """
    สร้างกระเป๋าเงินอัตโนมัติเมื่อสมัครสมาชิกใหม่
    """
    if created:
        Wallet.objects.create(member=instance)