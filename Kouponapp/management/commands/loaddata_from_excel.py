from datetime import datetime
from django.conf import settings
from django.contrib.admin import options
from Kouponapp.models import *
import os
from django.apps import apps
from django.db.models import *
from django.core.management.base import BaseCommand
from openpyxl import load_workbook
from Kouponapp.models import Member, Store

class Command(BaseCommand):
    help = "Load promotion data from data6.xlsx file"

    def handle(self, *args, **kwargs):
        # Path ของไฟล์ Excel
        #file_path = '/Users/yaneekumsudsang/Koupon/data4.xlsx'
        file_path = os.path.join(settings.BASE_DIR, 'Kouponapp/fixtures/data6.xlsx')

        # Load Excel workbook
        wb = load_workbook(filename=file_path)

        wm = wb['Member']
        for row in wm:
            values = [cell.value for cell in row]
            if values[0] != 'id':
                #id = values[0]
                #username = values[1]
                user = User.objects.create_user(values[1], values[5], str(values[6]), pk=values[0], first_name=values[2], last_name=values[3])
                member, created = Member.objects.get_or_create(user=user, phone=values[4], is_owner=bool(values[8]))

        #Store
        store_sheet = wb['Store']
        self.stdout.write("Loading Store Data...")

        for row in store_sheet.iter_rows(min_row=2, values_only=True):
            store_id, store_name, owner_id = row  # ดึงค่าจากคอลัมน์ id, store_name, owner_id

            # ตรวจสอบข้อมูลที่จำเป็น
            if not store_id or not store_name or not owner_id:
                self.stdout.write(f"Skipping row due to missing data: {row}")
                continue

            # ค้นหา Member ที่มี is_owner=True และ id ตรงกับ owner_id
            try:
                member = Member.objects.get(id=owner_id, is_owner=True)
            except Member.DoesNotExist:
                self.stdout.write(
                    f"Owner ID {owner_id} not found or not marked as owner. Skipping store: {store_name}.")
                continue

            # สร้างหรืออัปเดตข้อมูล Store โดยเชื่อมโยงกับ Owner ผ่าน member.user
            store_instance, created = Store.objects.update_or_create(
                id=store_id,
                defaults={
                    'store_name': store_name,
                    'owner': member,  # ใช้ Member แทนที่จะใช้ member.user
                }
            )

            # แสดงผลการทำงาน
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created store: {store_name} (Owner ID: {owner_id})"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated store: {store_name} (Owner ID: {owner_id})"))

        #Promotion
        promotion_sheet = wb['Promotion']
        for row in promotion_sheet.iter_rows(min_row=2, values_only=True):
            promotion_id, store_id, picture, cupsize, cups, discount, free, name, details, start, end, count, *_ = row
            # ค้นหา Store
            store = Store.objects.filter(id=store_id).first()
            if not store:
                self.stdout.write(f"Store ID {store_id} not found. Skipping promotion {name}.")
                continue

            # ตรวจสอบวันที่เริ่มและสิ้นสุด
            try:
                start = datetime.strptime(str(start).split()[0], '%Y-%m-%d').date()
            except ValueError as e:
                self.stdout.write(f"Invalid start date format for promotion ID {promotion_id}. Skipping... Error: {e}")
                continue

            try:
                end = datetime.strptime(str(end).split()[0], '%Y-%m-%d').date()
            except ValueError as e:
                self.stdout.write(f"Invalid end date format for promotion ID {promotion_id}. Skipping... Error: {e}")
                continue

            try:
                count = int(count) if count else 0  # ตรวจสอบว่ามีค่า และแปลงเป็นตัวเลข
            except ValueError as e:
                self.stdout.write(f"Invalid count value for promotion ID {promotion_id}. Skipping... Error: {e}")
                continue

            # สร้างหรืออัปเดตข้อมูล Promotion
            promotion_instance, created = Promotion.objects.get_or_create(
                id=promotion_id,
                defaults={
                    'store_id': store_id,
                    'picture': picture,
                    'cupsize': cupsize,
                    'cups': cups,
                    'discount': discount,
                    'free': free,
                    'name': name,
                    'details': details,
                    'start': start,
                    'end': end,
                    'count': count,
                }
            )

            if created:
                self.stdout.write(f"Created promotion: {name} for store: {store.store_name} with count: {count}")
            else:
                self.stdout.write(f"Promotion already exists: {name} with count: {count}")

        #Coupon
        coupon_sheet = wb['Coupon']
        for row in coupon_sheet.iter_rows(min_row=2, values_only=True):
            coupon_id, promotion_id, collect, member_id, promotion_count, qr_code_url = row

            # ค้นหา Promotion
            promotion = Promotion.objects.filter(id=promotion_id).first()
            if not promotion:
                self.stdout.write(f"Promotion ID {promotion_id} not found. Skipping coupon ID {coupon_id}.")
                continue

            # ตรวจสอบจำนวนคูปองที่ควรมี
            required_coupons = promotion.count  # จำนวนคูปองที่กำหนดในโปรโมชั่น
            current_coupons = Coupon.objects.filter(promotion=promotion).count()

            if current_coupons < required_coupons:
                # สร้างคูปองเพิ่ม
                for i in range(current_coupons + 1, required_coupons + 1):
                    # กำหนด username ของเจ้าของร้าน
                    store_owner = getattr(promotion.store.owner, 'user', None)
                    username = store_owner.username if store_owner else 'unknown'

                    # สร้าง URL ของ QR Code
                    qr_code_url = f"http://127.0.0.1/koupon/qr/{username}/use/{promotion.id}/{i}"

                    # สร้างคูปอง
                    coupon = Coupon.objects.create(
                        promotion=promotion,
                        promotion_count=i,  # promotion_count ตามลำดับ
                        collect=False,
                        member_id=None,  # หากยังไม่มีสมาชิกที่ใช้งานคูปอง
                        qr_code_url=qr_code_url  # เพิ่ม URL QR Code
                    )
                    self.stdout.write(
                        f"Created coupon ID {coupon.id} for promotion {promotion.id} with promotion_count {i}")
            elif current_coupons > required_coupons:
                # ลบคูปองส่วนเกินออก
                extra_coupons = Coupon.objects.filter(promotion=promotion).order_by('-id')[
                                :current_coupons - required_coupons]
                for coupon in extra_coupons:
                    coupon.delete()
                    self.stdout.write(f"Deleted extra coupon ID {coupon.id} for promotion {promotion.id}")
            else:
                self.stdout.write(
                    f"No changes required for promotion ID {promotion.id}. Coupons are already up to date.")

        self.stdout.write(self.style.SUCCESS("Data loaded successfully!"))