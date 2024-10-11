from django.core.management.base import BaseCommand
from openpyxl import load_workbook
from Kouponapp.models import Promotion

class Command(BaseCommand):
    help = "Load promotion data from data4.xlsx file"

    def handle(self, *args, **kwargs):
        # Path ของไฟล์ Excel
        file_path = '/Users/yaneekumsudsang/Downloads/data4.xlsx'

        # Load Excel workbook
        wb = load_workbook(filename=file_path)
        ws = wb.active  # สมมติว่า sheet แรกคือที่เราต้องการอ่าน

        # เริ่มอ่านข้อมูลจากแถวที่ 2
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
