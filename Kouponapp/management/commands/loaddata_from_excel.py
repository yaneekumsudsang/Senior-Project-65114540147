from datetime import datetime
from django.conf import settings
from django.contrib.admin import options
from Kouponapp.models import *
import os
from django.apps import apps
from django.db.models import *
from django.core.management.base import BaseCommand
from openpyxl import load_workbook

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
                member, created = Member.objects.get_or_create(user=user, phone=values[4])

        #Owner
        owner_sheet = wb['Owner']
        for row in owner_sheet.iter_rows(min_row=2, values_only=True):
            if len(row) < 5:  # ตรวจสอบว่าแถวมีข้อมูลขั้นต่ำ
                self.stdout.write(f"Skipping row due to insufficient columns: {row}")
                continue

            # ตัดให้เหลือเฉพาะคอลัมน์ที่จำเป็น
            owner_id, username, phone, email, password, *optional = row
            shop_logo = optional[0] if len(optional) > 0 else None  # ดึงค่า shop_logo ถ้ามี

            # สร้างหรืออัปเดตข้อมูล User
            user_instance, created = User.objects.get_or_create(
                id=owner_id,
                defaults={
                    'username': username,
                    'email': email,
                }
            )
            if created:
                user_instance.set_password(password)
                user_instance.save()
                self.stdout.write(f"Created owner user: {username}")
            else:
                self.stdout.write(f"Owner user already exists: {username}")

            # สร้างหรืออัปเดตข้อมูล Owner
            owner_instance, created = Owner.objects.get_or_create(
                user=user_instance,
                defaults={
                    'phone': phone,
                }
            )
            if created:
                self.stdout.write(f"Created owner profile for: {username}")
            else:
                owner_instance.phone = phone
                if shop_logo:
                    owner_instance.shop_logo = shop_logo  # อัปเดต shop_logo หากมี
                owner_instance.save()
                self.stdout.write(f"Updated owner profile for: {username}")

        #Store
        store_sheet = wb['Store']
        for row in store_sheet.iter_rows(min_row=2, values_only=True):
            store_id, store_name, owner_id = row

            # ค้นหา Owner
            owner = Owner.objects.filter(id=owner_id).first()
            if not owner:
                self.stdout.write(f"Owner ID {owner_id} not found. Skipping store {store_name}.")
                continue

            # สร้างหรืออัปเดตข้อมูล Store
            store_instance, created = Store.objects.get_or_create(
                id=store_id,
                defaults={
                    'store_name': store_name,
                    'owner_id': owner_id,
                }
            )
            if created:
                self.stdout.write(f"Created store: {store_name}")
            else:
                self.stdout.write(f"Store already exists: {store_name}")

        #Promotion
        promotion_sheet = wb['Promotion']
        for row in promotion_sheet.iter_rows(min_row=2, values_only=True):
            promotion_id, store_id, picture, cupsize, cups, discount, free, name, start, end, *_ = row
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
                    'start': start,
                    'end': end,
                }
            )
            if created:
                self.stdout.write(f"Created promotion: {name} for store: {store.store_name}")
            else:
                self.stdout.write(f"Promotion already exists: {name}")

        #Coupon
        coupon_sheet = wb['Coupon']
        for row in coupon_sheet.iter_rows(min_row=2, values_only=True):
            coupon_id, promotion_id, used, member_id = row

            # ค้นหา Promotion
            promotion = Promotion.objects.filter(id=promotion_id).first()
            if not promotion:
                self.stdout.write(f"Promotion ID {promotion_id} not found. Skipping coupon ID {coupon_id}.")
                continue

            # ค้นหา Member
            member = Member.objects.filter(id=member_id).first()
            if not member:
                self.stdout.write(f"Member ID {member_id} not found. Skipping coupon ID {coupon_id}.")
                continue

            # สร้างหรืออัปเดตข้อมูล Coupon
            coupon_instance, created = Coupon.objects.get_or_create(
                id=coupon_id,
                defaults={
                    'promotion': promotion,
                    'used': used,
                    'member_id': member,
                }
            )
            if created:
                self.stdout.write(f"Created coupon ID {coupon_id} for promotion {promotion.name}")
            else:
                self.stdout.write(f"Coupon ID {coupon_id} already exists.")

        self.stdout.write(self.style.SUCCESS("Data loaded successfully!"))

        # ดูที่  KhootClone week06 'load_xlsx.py'

        # {
        #   'id': 1,
        #   'username': 'a',
        #   'first_name': 'Abby',
        # }
        # เริ่มอ่านข้อมูลจากแถวที่ 2
        '''
        for row in ws.iter_rows(min_row=2, values_only=True):
            if len(row) >= 6:
                store_name, collection_number, cup_size, discount, coupon_name, expiration_date = row[:6]

                # ตรวจสอบว่า store_name มีหรือไม่ (เพื่อไม่ให้บันทึกข้อมูลที่ไม่สมบูรณ์)
                if not store_name:
                    continue

                # บันทึกข้อมูลเข้าสู่ Promotion model
                promotion = Promotion(
                    store_name=store_name,
                    collection_number=collection_number,
                    cup_size=cup_size,
                    discount=discount,
                    coupon_name=coupon_name,
                    expiration_date=expiration_date,  # ใช้ข้อมูลจาก Excel โดยตรง
                )
                promotion.save()

        self.stdout.write(self.style.SUCCESS('Successfully loaded data from Excel'))
        '''
