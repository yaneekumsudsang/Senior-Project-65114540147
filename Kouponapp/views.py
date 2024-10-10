from django.shortcuts import render
from .models import *
def promotions_view(request):
    # อ่านไฟล์ Excel
   # file_path = '/Users/yaneekumsudsang/Downloads/data2.xlsx'  # เส้นทางของไฟล์ Excel
   # df = pd.read_excel(file_path)
   #
   #  แปลง DataFrame เป็น List ของ Dictionary
   # promotions = df.to_dict(orient='records')
    data = Promotion.objects.all()
    # ส่งข้อมูลไปยัง template
    return render(request, 'home.html', {'data':data})
