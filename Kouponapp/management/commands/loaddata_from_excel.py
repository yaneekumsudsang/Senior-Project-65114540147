from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from openpyxl import load_workbook
from Kouponapp.models import Promotion
import os
from django.conf import settings
from Kouponapp.models import *

class Command(BaseCommand):
    help = "Load promotion data from data4.xlsx file"

    def handle(self, *args, **kwargs):
        # Path ของไฟล์ Excel
        #file_path = '/Users/yaneekumsudsang/Koupon/data4.xlsx'
        file_path = os.path.join(settings.BASE_DIR, 'Kouponapp/fixtures/data4-2.xlsx')

        # Load Excel workbook
        wb = load_workbook(filename=file_path)
        ws = wb.active  # สมมติว่า sheet แรกคือที่เราต้องการอ่าน

        ws = wb['Member']
        for row in ws:
            values = [cell.value for cell in row]
            if values[0] != 'id':
                #id = values[0]
                #username = values[1]
                user = User.objects.create_user(values[1], values[5], str(values[6]), pk=values[0], first_name=values[2], last_name=values[3])
                member, created = Member.objects.get_or_create(user=user, phone=values[4])

        ws = wb['Store']
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
