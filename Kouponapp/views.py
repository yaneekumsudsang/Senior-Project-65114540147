import logging

# Django built-in imports
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache

# Third-party imports
from qr_code.qrcode.utils import QRCodeOptions

# Local app imports
from .forms import RegisterForm, LoginForm, ProfileForm, PromotionForm
from .models import Member, Store, Promotion, Coupon

def promotions_view(request):
    data = Promotion.objects.all()[:5]
    return render(request, 'home.html', {'data':data})

def promotions_all(request):
    all_promotions = Promotion.objects.all()  # ดึงข้อมูลโปรโมชั่นทั้งหมด
    return render(request, 'promotions_all.html', {'all_promotions': all_promotions})

def promotions_member(request):
    member_promotions = Promotion.objects.all()[:10]  # ดึงข้อมูลทั้งหมดจาก Promotion
    return render(request, 'member.html', {'promotions_member': member_promotions})

def PromotionDetails(request, id):
    promotion = get_object_or_404(Promotion, id=id)
    return render(request, 'PromotionDetails.html', {'promotion': promotion})

@login_required
def promotion_list(request):
    # ดึงข้อมูลทั้งหมดจาก Promotion
    promotions = Promotion.objects.all()
    return render(request, 'promotion_list.html', {'promotions': promotions})

def UsedCoupons(request):
    promotions = Promotion.objects.all()
    return render(request, 'UsedCoupons.html', {'promotions':promotions})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Create user
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )
            user.save()

            # Display success message
            messages.success(request, 'สมัครสมาชิกสำเร็จ')
            return redirect('login')  # Redirect to login page
        else:
            messages.error(request, 'กรุณาตรวจสอบข้อมูลที่กรอก')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

logger = logging.getLogger(__name__)
def user_login(request):
    logger.info('Starting login process')  # Log when function starts
    print('starting login process')
    if request.method == 'POST':
        print('Received POST request')
        form = LoginForm(request.POST)
        print(form.is_valid())

        if form.is_valid():
            print('Form is valid')
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(username, password)

            print(f'Attempting to authenticate user: {username}')  # Debug username
            user = authenticate(request, username=username, password=password)

            if user is not None:
                print(f'User {username} authenticated successfully')
                login(request, user)  # Log in the user

                # ตรวจสอบว่า user เป็นเจ้าของร้าน
                if user.member.is_owner:
                    # ถ้าเป็นเจ้าของร้าน, redirect ไปยังหน้า 'owner/promotions'
                    return redirect('promotions_store')  # หน้าโปรโมชั่นของเจ้าของร้าน
                else:
                    # ถ้าไม่ใช่เจ้าของร้าน, redirect ไปยังหน้าโปรไฟล์หรือตามต้องการ
                    return redirect('home')  # หรือหน้าอื่นที่ต้องการ

                messages.success(request, 'เข้าสู่ระบบสำเร็จ')
                return redirect('promotions_member')  # Redirect to the home page

            else:
                logger.warning(f'Failed login attempt for username: {username}')
                messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
        else:
            logger.warning('Form validation failed')
            logger.debug(f'Form errors: {form.errors}')  # Debug form errors
            messages.error(request, 'กรุณากรอกข้อมูลให้ถูกต้อง')
    else:
        logger.info('Received GET request')
        form = LoginForm()

    logger.info('Rendering login form')
    return render(request, 'login.html', {'form': form})

@never_cache
def koupon_logout(request):
    logout(request)
    return redirect('home')


def profile_view(request):
    try:
        member = Member.objects.get(user=request.user)  # ดึงข้อมูลจาก Member
    except Member.DoesNotExist:
        member = None  # หากไม่พบข้อมูล Member ให้ใช้ None แทน

    if request.method == 'POST':
        # ใช้ instance ของ User และ Member ในฟอร์ม
        form = ProfileForm(request.POST, request.FILES, instance=request.user, member=member)
        if form.is_valid():
            form.save()  # บันทึกข้อมูลใน User และ Member
            messages.success(request, 'แก้ไขข้อมูลสำเร็จแล้ว')
            return redirect('profile')  # หรือหน้าโปรไฟล์
        else:
            messages.error(request, 'มีข้อผิดพลาด กรุณาตรวจสอบข้อมูลอีกครั้ง')
    else:
        # โหลดข้อมูลจาก User และ Member ลงในฟอร์ม
        form = ProfileForm(instance=request.user, member=member)

    return render(request, 'profile.html', {'form': form})

@login_required
def promotions_store(request):
    # ตรวจสอบว่า user เป็นเจ้าของร้าน (is_owner=True)
    if not request.user.member.is_owner:
        # ถ้าไม่ใช่เจ้าของร้าน ให้ redirect ไปยังหน้าอื่น
        return redirect('promotions_store')  # หรือไปยังหน้าอื่นที่คุณต้องการ

    # ดึงข้อมูลร้านที่เจ้าของมี
    store = Store.objects.filter(owner=request.user.member).first()

    # ถ้าพบร้านที่เจ้าของมี
    if store:
        # ดึงโปรโมชันที่เชื่อมโยงกับร้านของเจ้าของ
        promotions = Promotion.objects.filter(store=store)
    else:
        promotions = []

    # ส่งข้อมูลโปรโมชันไปยังเทมเพลต
    return render(request, 'promotions_store.html', {'promotions': promotions})

@login_required
def used_coupons_by_member_store(request):
    # ดึงข้อมูลคูปองที่สมาชิกใช้
    used_coupons = Coupon.objects.filter(member_id=request.user.member, used=True).select_related('promotion', 'promotion__store')

    # ส่งข้อมูลไปยังเทมเพลต
    return render(request, 'used_coupons_by_member_store.html', {'used_coupons': used_coupons})

def CouponDesign_Store(request, id=None):
    if id:  # แก้ไขข้อมูลคูปองที่มีอยู่
        promotion = get_object_or_404(Promotion, id=id)
    else:  # สร้างคูปองใหม่
        promotion = None

    if request.method == 'POST':
        form = PromotionForm(request.POST, request.FILES, instance=promotion)
        if form.is_valid():
            promotion = form.save()  # บันทึกข้อมูลลงในฐานข้อมูล
            return redirect('CouponPreview', id=promotion.id)  # ไปยังหน้าตัวอย่างคูปอง
    else:
        form = PromotionForm(instance=promotion)

    return render(request, 'CouponDesign_Store.html', {'form': form, 'promotion': promotion})
def CreateQRcode_Store(request, promotion_id):
    # ดึงข้อมูล Promotion จากฐานข้อมูล
    promotion = get_object_or_404(Promotion, id=promotion_id)

    # สร้าง URL สำหรับ QR Code
    qr_data = f"http://yourwebsite.com/promotions/{promotion.id}/"

    # ตั้งค่าการสร้าง QR Code
    qr_options = QRCodeOptions(size="L", border=4, error_correction="L")

    # ส่งข้อมูล QR Code ไปยัง Template
    return render(request, "CreateQRcode_Store.html", {
        "promotion": promotion,
        "qr_data": qr_data,
        "qr_options": qr_options,
    })

# ฟังก์ชันแสดงหน้าคูปอง
def view_promotion(request, promotion_id):
    # ดึงข้อมูล Promotion จากฐานข้อมูล
    promotion = get_object_or_404(Promotion, id=promotion_id)

    # ส่งข้อมูลไปยัง Template
    return render(request, "ScanQRcodeAddCoupons.html", {
        "promotion": promotion,
    })