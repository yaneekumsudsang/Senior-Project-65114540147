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
from decimal import Decimal
import traceback
from decimal import Decimal
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError

class Command(BaseCommand):
    help = "Load promotion data from data7.xlsx file"

    def handle(self, *args, **kwargs):
        # Path ของไฟล์ Excel
        #file_path = '/Users/yaneekumsudsang/Koupon/data4.xlsx'
        file_path = os.path.join(settings.BASE_DIR, 'Kouponapp/fixtures/data7.xlsx')

        # Load Excel workbook
        wb = load_workbook(filename=file_path)

        print('load "Member"')
        wm = wb['Member']
        for row in wm.iter_rows(min_row=2, values_only=True):
            if row[0]:
                user = User.objects.create_user(row[1], row[5], str(row[6]), pk=row[0], first_name=row[2], last_name=row[3])
                member, created = Member.objects.get_or_create(pk=row[0], user=user, phone=row[4], is_owner=bool(row[8]))

        store_sheet = wb['Store']
        self.stdout.write("Loading Store Data...")

        for row in store_sheet.iter_rows(min_row=2, values_only=True):
            store_id, store_name, owner_id = row

            # ตรวจสอบข้อมูลที่จำเป็น
            if not store_id or not store_name or not owner_id:
                self.stdout.write(f"Skipping row due to missing data: {row}")
                continue

            try:
                # ค้นหา Member ที่เป็นเจ้าของร้าน
                member = Member.objects.get(id=owner_id, is_owner=True)
            except Member.DoesNotExist:
                self.stdout.write(
                    f"Owner ID {owner_id} not found or not marked as owner. Skipping store: {store_name}.")
                continue

            try:
                # สร้างหรืออัปเดตร้านค้า
                store_instance, created = Store.objects.update_or_create(
                    id=store_id,
                    defaults={'store_name': store_name, 'owner': member}
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created store: {store_name} (Owner ID: {owner_id})"))
                else:
                    self.stdout.write(self.style.WARNING(f"Updated store: {store_name} (Owner ID: {owner_id})"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing store {store_name}: {str(e)}"))

        #Promotion
        print('load "Promotion"')
        promotion_sheet = wb['Promotion']
        for row in promotion_sheet.iter_rows(min_row=2, values_only=True):
            promotion_id, store_id, picture, cupsize, cups, discount, free, name, details, start, end, count = row
            print(row)
            if promotion_id:
                store = Store.objects.get(pk=store_id)
                p, created = Promotion.objects.get_or_create(
                        pk=promotion_id,
                        store=store,
                        name=name,
                        picture=picture,
                        cupsize=cupsize,
                        cups=cups,
                        discount=discount,
                        free=free,
                        details=details,
                        start=start,
                        end=end,
                        count=count
                )
            else:
                break


        # โหลดข้อมูลคูปองจากชีต Excel
        print('โหลดข้อมูลคูปองจากชีต Excel')
        coupon_sheet = wb['Coupon']
        for row in coupon_sheet.iter_rows(min_row=2, values_only=True):
            print(row)
            coupon_id, promotion_id, promotion_count, collect, member_id, collect_qr_code_url, use_qr_code_url, *_ = row

            if promotion_id:
                # ค้นหา Promotion
                #print('promotion_id=', promotion_id)
                promotion = Promotion.objects.get(pk=promotion_id)

                # ค้นหาคูปองที่มีอยู่แล้วในฐานข้อมูล
                coupon = Coupon.objects.filter(promotion=promotion, promotion_count=promotion_count).first()

                # กำหนด username ของเจ้าของร้าน
                store_owner = getattr(promotion.store.owner, 'user', None)
                username = store_owner.username if store_owner else 'unknown'

                # กำหนดค่า QR Code URL
                generated_collect_qr_code_url = f"http://127.0.0.1/koupon/qr/{promotion.id}/collec/{promotion_count}/{coupon_id}/"
                generated_use_qr_code_url = f"http://127.0.0.1/koupon/qr/{promotion.id}/use/{promotion_count}/{coupon_id}/"

                if not coupon:
                    # คูปองยังไม่มีในระบบ ให้สร้างใหม่
                    coupon = Coupon.objects.create(
                        promotion=promotion,
                        promotion_count=promotion_count,
                        collect=bool(collect),
                        member=Member.objects.get(pk=member_id),
                        collect_qr_code_url=generated_collect_qr_code_url,
                        use_qr_code_url=generated_use_qr_code_url
                    )
                    self.stdout.write(
                        f"Created new coupon ID {coupon.id} for promotion {promotion.id} (count {promotion_count})")
                else:
                    # อัปเดตข้อมูลของคูปองให้ตรงกับไฟล์ Excel
                    updated_fields = {}
                    if coupon.collect_qr_code_url != generated_collect_qr_code_url:
                        updated_fields['collect_qr_code_url'] = generated_collect_qr_code_url
                    if coupon.use_qr_code_url != generated_use_qr_code_url:
                        updated_fields['use_qr_code_url'] = generated_use_qr_code_url
                    if coupon.collect != bool(collect):
                        updated_fields['collect'] = bool(collect)
                    if coupon.member_id != (member_id if member_id else None):
                        updated_fields['member_id'] = member_id if member_id else None

                    if updated_fields:
                        for field, value in updated_fields.items():
                            setattr(coupon, field, value)
                        coupon.save()
                        self.stdout.write(
                            f"Updated coupon ID {coupon.id} for promotion {promotion.id} (count {promotion_count})")
                    else:
                        self.stdout.write(f"No updates required for coupon ID {coupon.id}")

        self.stdout.write(self.style.SUCCESS("Data loaded successfully!"))
