import logging
from datetime import timezone

import numpy as np
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

import segno
import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import segno
import io
import base64
from .models import Member, Store, Promotion, Coupon
from .forms import PromotionForm
import cv2
from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse
from pyzbar.pyzbar import decode
import numpy as np
from .models import ScannedQRCode
from django.utils import timezone
from django.http import JsonResponse

def promotions_view(request):
    data = Promotion.objects.all()[:5]
    return render(request, 'home.html', {'data':data})

def promotions_all(request):
    all_promotions = Promotion.objects.all()  # ดึงข้อมูลโปรโมชั่นทั้งหมด
    return render(request, 'promotions_all.html', {'all_promotions': all_promotions})

def promotions_member(request):
    member_promotions = Promotion.objects.all()[:10]  # ดึงข้อมูลทั้งหมดจาก Promotion
    return render(request, 'member.html', {'promotions_member': member_promotions})

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

@login_required
def CouponDesign_Store(request, id=None):
    # ดึงร้านค้าของผู้ใช้งาน
    member = get_object_or_404(Member, user=request.user)
    store = get_object_or_404(Store, owner=member)

    if id:  # แก้ไขโปรโมชั่นที่มีอยู่
        promotion = get_object_or_404(Promotion, id=id)
    else:  # สร้างโปรโมชั่นใหม่
        promotion = None

    if request.method == 'POST':
        form = PromotionForm(request.POST, request.FILES, instance=promotion)
        if form.is_valid():
            # บันทึก Promotion
            promotion = form.save(commit=False)
            promotion.store = store
            promotion.save()

            # จัดการคูปองตามจำนวน `count` ที่กำหนด
            desired_coupon_count = promotion.count or 1  # ถ้า `count` ไม่มีค่า ให้ใช้ค่า 1
            existing_coupons = Coupon.objects.filter(promotion=promotion)

            # ลบคูปองที่เกินจำนวน `count`
            if existing_coupons.count() > desired_coupon_count:
                excess_coupons = existing_coupons[desired_coupon_count:]
                excess_coupons.delete()

            # สร้างคูปองใหม่ถ้าจำนวนปัจจุบันไม่เพียงพอ
            for i in range(existing_coupons.count(), desired_coupon_count):
                Coupon.objects.create(
                    promotion=promotion,
                    promotion_count=i + 1,  # กำหนดเลขลำดับของคูปอง
                    used=False
                )

            # เปลี่ยนเส้นทางไปยัง CouponPreview
            return redirect('CouponPreview', promotion_id=promotion.id)
        else:
            print("Form Errors:", form.errors)  # แสดงข้อผิดพลาดของฟอร์ม
    else:
        form = PromotionForm(instance=promotion)

    return render(request, 'CouponDesign_Store.html', {'form': form, 'promotion': promotion})

def generate_coupon_qr_data(promotion, coupon_number):
    qr_data = {
        'promotion_id': promotion.id,
        'coupon_number': coupon_number,
        'store_name': promotion.store.store_name,
        'promotion_name': promotion.name,
        'valid_until': promotion.end.strftime('%Y-%m-%d'),
        'discount': float(promotion.discount) if promotion.discount else 0,
        'free_cups': promotion.free if promotion.free else 0
    }
    return str(qr_data)


@login_required
def CouponPreview(request, promotion_id):
    promotion = get_object_or_404(Promotion, id=promotion_id)
    qr_codes = []

    # Get base URL
    base_url = request.build_absolute_uri('/').rstrip('/')

    # Get or create coupons
    existing_coupons = Coupon.objects.filter(promotion=promotion)
    existing_count = existing_coupons.count()
    desired_coupon_count = promotion.count or 1

    if existing_count < desired_coupon_count:
        new_coupons_needed = desired_coupon_count - existing_count

        for i in range(new_coupons_needed):
            new_promotion_count = existing_count + i + 1

            # Create new coupon
            coupon = Coupon.objects.create(
                promotion=promotion,
                promotion_count=new_promotion_count,
                collect=False
            )

            # Generate QR URL and save it
            qr_url = f"{base_url}/koupon/qr/{promotion.store.id}/{promotion.id}/{coupon.id}/"
            coupon.qr_code_url = qr_url
            coupon.save()  # This will trigger the QR code generation

            # Add QR code info to the list for display
            qr_codes.append({
                'coupon': coupon,
                'qr_image_path': f"qr_codes/qr_code_{promotion.id}_{coupon.id}.png",
            })

    # Handle existing coupons
    for coupon in existing_coupons:
        if not coupon.qr_code_url:
            qr_url = f"{base_url}/koupon/qr/{promotion.store.id}/{promotion.id}/{coupon.id}/"
            coupon.qr_code_url = qr_url
            coupon.save()  # This will trigger the QR code generation

        qr_codes.append({
            'coupon': coupon,
            'qr_image_path': f"qr_codes/qr_code_{promotion.id}_{coupon.id}.png",
        })

    return render(request, 'CouponPreview.html', {
        'promotion': promotion,
        'qr_codes': qr_codes,
    })

def generate_qr_base64(qr_url):
    """
    ฟังก์ชันช่วยสร้าง QR Code ในรูปแบบ Base64
    """
    qr = segno.make(qr_url)
    buffer = io.BytesIO()
    qr.save(buffer, kind="png", scale=10)
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    return qr_base64

class CameraStream(str):
    def __init__(self):
        self.camera = cv2.VideoCapture(0)

    def get_frames(self):
        while True:
            # Capture frame-by-frame
            success, frame = self.camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                color_image = np.asanyarray(frame)
                if decode(color_image):
                    for qrcode in decode(color_image):
                        barcode_data = (qrcode.data).decode('utf-8')
                else:
                    frame = buffer.tobytes()
                    #hasil2 = b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + barcode_frame + b'\r\n\r\n'
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def camera_feed(request):
    stream = CameraStream()
    frames = stream.get_frames()
    return StreamingHttpResponse(frames, content_type='multipart/x-mixed-replace; boundary=frame')

def detect(request):
    stream = CameraStream()
    success, frame = stream.camera.read()
    if success:
        status = True
    else:
        status = False

    return render(request, 'scan_qrcode.html', context={'cam_status': status})

@login_required
def Collect_coupons(request, store_id, promotion_id, coupon_id):
    """ฟังก์ชันสำหรับการสแกน QR Code และเก็บคูปอง"""
    try:
        # ดึงข้อมูลร้านค้า, โปรโมชั่น และคูปอง
        store = Store.objects.get(pk=store_id)
        promotion = Promotion.objects.get(id=promotion_id, store=store)
        coupon = Coupon.objects.get(id=coupon_id, promotion=promotion)

        # บันทึกการสแกน QR Code
        scanned_qr = ScannedQRCode.objects.create(
            scanned_text=coupon.id,
            is_url=False,
        )

        # ดึงข้อมูลชื่อผู้ใช้จาก `request.user`
        username = request.user.username

        if coupon.used:
            messages.error(request, f"คูปองนี้ถูกใช้งานไปแล้วโดย {username}")
        elif promotion.end < timezone.now().date():
            messages.error(request, f"คูปองนี้หมดอายุแล้ว โดย {username}")
        else:
            # อัปเดตสถานะคูปอง
            coupon.used = True
            coupon.used_at = timezone.now()
            coupon.save()

            messages.success(request, f"คูปองถูกใช้งานเรียบร้อยแล้วโดย {username}!")

    except Store.DoesNotExist:
        messages.error(request, "ไม่พบร้านค้านี้ในระบบ")
    except Promotion.DoesNotExist:
        messages.error(request, "ไม่พบโปรโมชั่นนี้ในระบบ")
    except Coupon.DoesNotExist:
        messages.error(request, "ไม่พบคูปองนี้ในระบบ")

    # เปลี่ยนไปยังหน้าสะสมคูปอง
    return redirect('my_coupons')

@login_required
def my_coupons(request):
    """แสดงรายการคูปองที่ผู้ใช้สะสม"""
    # ดึงรายการคูปองที่เกี่ยวข้องกับผู้ใช้ปัจจุบัน
    scanned_qrcodes = ScannedQRCode.objects.all()  # หากต้องการดึงข้อมูลการสแกนทั้งหมด

    # ดึงข้อมูลชื่อผู้ใช้ที่เกี่ยวข้องกับการสแกน
    username = request.user.username

    # ดึงคูปองทั้งหมดที่เกี่ยวข้อง
    coupons = Coupon.objects.filter(id__in=scanned_qrcodes.values_list('scanned_text', flat=True))

    return render(request, 'my_coupons.html', {'coupons': coupons, 'username': username})

def PromotionDetails(request, store_id, promotion_id, coupon_id):
    promotion = get_object_or_404(Promotion, id=promotion_id, store_id=store_id)
    coupon = get_object_or_404(Coupon, id=coupon_id, promotion=promotion)

    # เส้นทางรูปภาพใน static/qr_codes
    image_path = f"qr_codes/{promotion.id}.png"

    return render(request, 'PromotionDetails.html', {
        'promotion': promotion,
        'coupon': coupon,
        'image_path': image_path,
    })

def PromotionDetailsStore(request, promotion_id, coupon_id):
    # ดึงข้อมูล Promotion และ Coupon ที่เกี่ยวข้อง
    promotion = get_object_or_404(Promotion, id=promotion_id)
    coupon = get_object_or_404(Coupon, id=coupon_id, promotion=promotion)

    return render(request, 'PromotionDetailsStore.html', {
        'promotion': promotion,
        'coupon': coupon,
    })

#@login_required
def list_member_collect_coupons(request):
    # Query coupons with related promotion and store data
    used_coupons = Coupon.objects.filter(used=True).select_related(
        'promotion',
        'promotion__store',
        'member'
    ).order_by('-promotion__end')  # Order by expiration date

    # Add analytics data to the context
    context = {
        'used_coupons': used_coupons,
        'total_coupons': used_coupons.count(),
        'total_stores': used_coupons.values('promotion__store').distinct().count(),
        'total_promotions': used_coupons.values('promotion').distinct().count(),
    }

    return render(request, 'list_member_collect_coupons.html', context)
