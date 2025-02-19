# Standard library imports
import json
import logging
import os
import io
import base64
from datetime import timezone

# Third-party imports
import numpy as np
import cv2
from pyzbar.pyzbar import decode
from qr_code.qrcode.utils import QRCodeOptions

# Django built-in imports
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.models import Count, Sum, Q, F
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.cache import never_cache

# Local app imports
from .forms import RegisterForm, LoginForm, ProfileForm, PromotionForm
from django.shortcuts import render, get_object_or_404, redirect
from .forms import MemberUpdateForm, StoreOwnershipRequestForm

from django.db.models import Count, Q, Case, When, BooleanField, F
from .models import *
from django.utils import timezone
from datetime import date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q, Sum
from .models import Store, Promotion, Coupon
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Coupon, ScannedQRCode
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
from .models import Wallet, Transaction
from django.utils import timezone
from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Member, Wallet, Store, Promotion, Coupon, Transaction, ScannedQRCode


def promotions_view(request):
    data = Promotion.objects.all()[:5]
    return render(request, 'home.html', {'data':data})

def promotions_all(request):
    all_promotions = Promotion.objects.all()  # ดึงข้อมูลโปรโมชั่นทั้งหมด
    return render(request, 'promotions_all.html', {'all_promotions': all_promotions})

def promotions_all_details(request, store_id, promotion_id):
    promotion = get_object_or_404(Promotion, id=promotion_id, store_id=store_id)
    coupons = Coupon.objects.filter(promotion=promotion)
    stores = Store.objects.all()

    return render(request, 'PromotionsAllDetails.html', {
        'promotion': promotion,
        'coupons': coupons,
        'stores': stores,
    })

def promotions_member(request):
    # ดึงข้อมูลโปรโมชั่นสำหรับสมาชิก
    member_promotions = Promotion.objects.all()[:10]

    # ดึงข้อมูลคูปองที่ถูกใช้และนับจำนวนคูปองที่ถูกใช้ในแต่ละร้านค้า (เฉพาะผู้ใช้ที่เข้าสู่ระบบ)
    used_coupons_by_store = Coupon.objects.filter(
        used=True,  # คูปองที่ถูกใช้แล้ว
        member=request.user.member  # คูปองที่ถูกใช้โดยผู้ใช้ที่เข้าสู่ระบบ
    ).values(
        'promotion__store__store_name'  # ชื่อร้านค้า
    ).annotate(
        total_used=Count('id')  # นับจำนวนคูปองที่ถูกใช้
    )

    # สร้าง dictionary เพื่อเก็บข้อมูลร้านค้าและจำนวนคูปองที่ถูกใช้
    store_data = {item['promotion__store__store_name']: item['total_used'] for item in used_coupons_by_store}

    return render(request, 'member.html', {
        'promotions_member': member_promotions,
        'store_data': store_data  # ส่งข้อมูลร้านค้าและจำนวนคูปองที่ถูกใช้ไปยังเทมเพลต
    })

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

            # creat member
            member = Member(user=user, phone=phone)
            member.save()

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

                if user.is_superuser:
                    return redirect('admin_member_management')

                # ตรวจสอบว่า user เป็นเจ้าของร้าน
                if user.member.is_owner:
                    # ถ้าเป็นเจ้าของร้าน, redirect ไปยังหน้า 'owner/promotions'
                    return redirect('promotions_store')  # หน้าโปรโมชั่นของเจ้าของร้าน
                else:
                    # ถ้าไม่ใช่เจ้าของร้าน, redirect ไปยังหน้าโปรไฟล์หรือตามต้องการ
                    return redirect('promotions_member')  # หรือหน้าอื่นที่ต้องการ

                messages.success(request, 'เข้าสู่ระบบสำเร็จ')
                return redirect('home')  # Redirect to the home page

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

def koupon_logout(request):
    logout(request)
    return redirect('home')

@login_required
def profile_member(request):
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        member = None

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user, member=member)
        if form.is_valid():
            form.save()

            # สร้างหรืออัพเดท Member
            if member is None:
                member = Member.objects.create(user=request.user)

            # บันทึกเบอร์โทรศัพท์
            if 'phone' in form.cleaned_data:
                member.phone = form.cleaned_data['phone']

            # บันทึกรูปโปรไฟล์
            if 'profile_img' in request.FILES:
                member.profile_img = request.FILES['profile_img']

            member.save()

            messages.success(request, 'แก้ไขข้อมูลสำเร็จแล้ว')
            return redirect('profile_member')
        else:
            messages.error(request, 'มีข้อผิดพลาด กรุณาตรวจสอบข้อมูลอีกครั้ง')
    else:
        form = ProfileForm(instance=request.user, member=member)

    context = {
        'form': form,
        'member': member,
        'user': request.user,
        'store_request': StoreOwnerRequest.objects.filter(user=request.user).first()
    }

    return render(request, 'profile_member.html', context)

@login_required
def profile_store(request):
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        member = None

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user, member=member)
        if form.is_valid():
            form.save()

            # สร้างหรืออัพเดท Member
            if member is None:
                member = Member.objects.create(user=request.user)

            # บันทึกเบอร์โทรศัพท์
            if 'phone' in form.cleaned_data:
                member.phone = form.cleaned_data['phone']

            # บันทึกรูปโปรไฟล์
            if 'profile_img' in request.FILES:
                member.profile_img = request.FILES['profile_img']

            member.save()

            messages.success(request, 'แก้ไขข้อมูลสำเร็จแล้ว')
            return redirect('profile_store')
        else:
            messages.error(request, 'มีข้อผิดพลาด กรุณาตรวจสอบข้อมูลอีกครั้ง')
    else:
        form = ProfileForm(instance=request.user, member=member)

    context = {
        'form': form,
        'member': member,
        'user': request.user,
        'store_request': StoreOwnerRequest.objects.filter(user=request.user).first()
    }

    return render(request, 'profile_store.html', context)

@login_required
def promotions_store(request):
    if not request.user.member.is_owner:
        return redirect('home')

    store = Store.objects.filter(owner=request.user.member).first()

    if store:
        # ดึงข้อมูลโปรโมชั่นทั้งหมดของร้าน
        promotions = Promotion.objects.filter(store=store)
        promotion_stats = []

        for promotion in promotions:
            coupons = Coupon.objects.filter(promotion=promotion)
            total_coupons = coupons.count()

            if total_coupons > 0:
                collected_coupons = coupons.filter(collect=True).count()
                uncollected_coupons = total_coupons - collected_coupons
                used_coupons = coupons.filter(used=True).count()
                unused_coupons = total_coupons - used_coupons

                collected_percentage = (collected_coupons / total_coupons) * 100
                uncollected_percentage = (uncollected_coupons / total_coupons) * 100
                used_percentage = (used_coupons / total_coupons) * 100
                unused_percentage = (unused_coupons / total_coupons) * 100

                promotion_stats.append({
                    'name': promotion.name,
                    'total_coupons': total_coupons,
                    'collected_coupons': collected_coupons,
                    'uncollected_coupons': uncollected_coupons,
                    'used_coupons': used_coupons,
                    'unused_coupons': unused_coupons,
                    'collected_percentage': collected_percentage,
                    'uncollected_percentage': uncollected_percentage,
                    'used_percentage': used_percentage,
                    'unused_percentage': unused_percentage,
                })

        context = {
            'promotions': promotions,
            'promotion_stats': promotion_stats,
            'promotion_stats_json': json.dumps(promotion_stats),
            'has_data': len(promotion_stats) > 0
        }
    else:
        context = {
            'promotion_stats': [],
            'promotion_stats_json': '[]',
            'has_data': False
        }

    return render(request, 'promotions_store.html', context)

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
                    collect=False
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
                collect=False,
                used=False
            )

            # Generate Collection QR URL
            collect_url = f"{base_url}/koupon/qr/{promotion.store.id}/collec/{promotion.id}/{coupon.id}/"

            # Generate Use QR URL
            use_url = f"{base_url}/koupon/qr/{promotion.store.id}/use/{promotion.id}/{coupon.id}/"

            # Save the collection and use URLs
            coupon.collect_qr_code_url = collect_url
            coupon.use_qr_code_url = use_url

            # Generate both QR codes
            collect_qr = segno.make(collect_url)
            use_qr = segno.make(use_url)

            # Save QR codes to static/qr_codes
            static_path = os.path.join(settings.BASE_DIR, 'static', 'qr_codes')
            os.makedirs(static_path, exist_ok=True)

            collect_file_path = os.path.join(static_path, f'collect_qr_{promotion.id}_{coupon.id}.png')
            use_file_path = os.path.join(static_path, f'use_qr_{promotion.id}_{coupon.id}.png')

            collect_qr.save(collect_file_path, scale=10)
            use_qr.save(use_file_path, scale=10)

            # Save QR code images to the database
            with io.BytesIO() as collect_buffer, io.BytesIO() as use_buffer:
                collect_qr.save(collect_buffer, kind='png', scale=10)
                collect_buffer.seek(0)
                coupon.collect_qr_code_image.save(f'collect_qr_{promotion.id}_{coupon.id}.png', ContentFile(collect_buffer.getvalue()), save=False)

                use_qr.save(use_buffer, kind='png', scale=10)
                use_buffer.seek(0)
                coupon.use_qr_code_url_image.save(f'use_qr_{promotion.id}_{coupon.id}.png', ContentFile(use_buffer.getvalue()), save=False)

            coupon.save()

            # Add QR codes info to the list for display
            qr_codes.append({
                'coupon': coupon,
                'collect_qr_path': f"qr_codes/collect_qr_{promotion.id}_{coupon.id}.png",
                'use_qr_path': f"qr_codes/use_qr_{promotion.id}_{coupon.id}.png",
            })

    # Handle existing coupons
    for coupon in existing_coupons:
        collect_url = f"{base_url}/koupon/qr/{promotion.store.id}/collec/{promotion.id}/{coupon.id}/"
        use_url = f"{base_url}/koupon/qr/{promotion.store.id}/use/{promotion.id}/{coupon.id}/"

        if not coupon.collect_qr_code_url:
            coupon.collect_qr_code_url = collect_url
        if not coupon.use_qr_code_url:
            coupon.use_qr_code_url = use_url

        # Generate both QR codes if they don't exist
        collect_qr = segno.make(collect_url)
        use_qr = segno.make(use_url)

        static_path = os.path.join(settings.BASE_DIR, 'static', 'qr_codes')
        os.makedirs(static_path, exist_ok=True)

        collect_file_path = os.path.join(static_path, f'collect_qr_{promotion.id}_{coupon.id}.png')
        use_file_path = os.path.join(static_path, f'use_qr_{promotion.id}_{coupon.id}.png')

        if not os.path.exists(collect_file_path):
            collect_qr.save(collect_file_path, scale=10)
        if not os.path.exists(use_file_path):
            use_qr.save(use_file_path, scale=10)

        # Save QR code images to the database if not already saved
        if not coupon.collect_qr_code_image:
            with io.BytesIO() as collect_buffer:
                collect_qr.save(collect_buffer, kind='png', scale=10)
                collect_buffer.seek(0)
                coupon.collect_qr_code_image.save(f'collect_qr_{promotion.id}_{coupon.id}.png', ContentFile(collect_buffer.getvalue()), save=False)

        if not coupon.use_qr_code_url_image:
            with io.BytesIO() as use_buffer:
                use_qr.save(use_buffer, kind='png', scale=10)
                use_buffer.seek(0)
                coupon.use_qr_code_url_image.save(f'use_qr_{promotion.id}_{coupon.id}.png', ContentFile(use_buffer.getvalue()), save=False)

        coupon.save()

        qr_codes.append({
            'coupon': coupon,
            'collect_qr_path': f"qr_codes/collect_qr_{promotion.id}_{coupon.id}.png",
            'use_qr_path': f"qr_codes/use_qr_{promotion.id}_{coupon.id}.png",
        })

    return render(request, 'CouponPreview.html', {
        'promotion': promotion,
        'qr_codes': qr_codes,
    })

def generate_qr_base64(qr_url):
    """
    Helper function to generate QR Code in Base64 format
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

from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Member, Wallet, Store, Promotion, Coupon, Transaction, ScannedQRCode

@login_required
def Collect_coupons(request, store_id, promotion_id, coupon_id):
    try:
        # ดึงข้อมูลสมาชิกและกระเป๋าเงิน
        current_member = Member.objects.get(user=request.user)
        customer_wallet, created = Wallet.objects.get_or_create(member=current_member)

        # ดึงข้อมูลร้านค้าและกระเป๋าเงินเจ้าของร้าน
        store = Store.objects.get(pk=store_id)
        store_owner = store.owner
        owner_wallet, created = Wallet.objects.get_or_create(member=store_owner)

        # ดึงข้อมูลโปรโมชั่นและคูปอง
        promotion = Promotion.objects.get(id=promotion_id, store=store)
        coupon = Coupon.objects.get(id=coupon_id, promotion=promotion)

        # บันทึกการสแกน QR Code
        ScannedQRCode.objects.create(
            scanned_text=str(coupon.id),
            is_url=False,
        )

        # ตรวจสอบเงื่อนไขคูปองว่าถูกใช้ไปแล้วหรือไม่
        if coupon.collect:
            messages.error(request, "คูปองนี้ถูกสะสมไปแล้ว")
            return redirect('my_coupons')

        if promotion.end < timezone.now().date():
            messages.error(request, "คูปองนี้หมดอายุแล้ว")
            return redirect('my_coupons')

        # นับจำนวนคูปองที่สมาชิกสะสมไปแล้ว
        collected_count = Coupon.objects.filter(
            promotion=promotion,
            member=current_member,
            collect=True
        ).count()

        # ตรวจสอบว่าเป็นโปรโมชั่น **สะสมครบได้ฟรี** หรือ **สะสมครบได้ส่วนลด**
        is_free_reward = bool(promotion.free)  # มีของฟรีไหม
        is_discount_reward = bool(promotion.discount)  # มีส่วนลดไหม

        # ✅ **ตอนสะสม ให้ตัดเงินเต็มจำนวนเสมอ**
        price_to_deduct = promotion.price

        # ตรวจสอบว่าสมาชิกมียอดเงินพอหรือไม่
        if customer_wallet.balance < price_to_deduct:
            messages.error(request, f"ยอดเงินไม่เพียงพอ ต้องการ ฿{price_to_deduct:,.2f} แต่มี ฿{customer_wallet.balance:,.2f}")
            return redirect('my_wallet')

        # ทำธุรกรรมทั้งหมดในคราวเดียว
        with transaction.atomic():
            # หักเงินเต็มจำนวนจากลูกค้า และเพิ่มเงินให้ร้านค้า
            if not customer_wallet.deduct_balance(price_to_deduct):
                messages.error(request, "เกิดข้อผิดพลาดในการหักเงิน")
                return redirect('my_wallet')

            owner_wallet.add_balance(price_to_deduct)

            # บันทึกประวัติการทำรายการของลูกค้า
            Transaction.objects.create(
                wallet=customer_wallet,
                amount=price_to_deduct,
                transaction_type='DEBIT',
                description=f'สะสมคูปอง {promotion.name} ที่ร้าน {store.store_name}'
            )

            # บันทึกประวัติการทำรายการของร้านค้า
            Transaction.objects.create(
                wallet=owner_wallet,
                amount=price_to_deduct,
                transaction_type='CREDIT',
                description=f'รับเงินจากการสะสมคูปอง {promotion.name} โดย {current_member.user.username}'
            )

            # อัพเดทสถานะคูปอง
            coupon.collect = True
            coupon.collected_at = timezone.now()
            coupon.member = current_member
            coupon.save()

        # แสดงข้อความตามสถานะการสะสม
        if promotion.cups and collected_count + 1 >= promotion.cups:
            if is_free_reward:
                messages.success(request,
                                 f"สะสมคูปองและชำระเงิน ฿{price_to_deduct:,.2f} สำเร็จ! "
                                 f"สะสมครบ {promotion.cups} แก้ว! "
                                 f"รับฟรี {promotion.free} แก้ว!")
            elif is_discount_reward:
                messages.success(request,
                                 f"สะสมคูปองและชำระเงิน ฿{price_to_deduct:,.2f} สำเร็จ! "
                                 f"สะสมครบ {promotion.cups} แก้ว! "
                                 f"คุณได้รับส่วนลด {promotion.discount}% สำหรับการใช้คูปองครั้งต่อไป")
        else:
            messages.success(request,
                             f"สะสมคูปองและชำระเงิน ฿{price_to_deduct:,.2f} สำเร็จ! "
                             f"สะสมอีก {promotion.cups - (collected_count + 1)} แก้วเพื่อรับสิทธิพิเศษ")

    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาดในการทำรายการ: {str(e)}")

    return redirect('my_coupons')

@login_required
def my_coupons(request):
    """แสดงรายการคูปองที่ผู้ใช้สะสมและยังไม่หมดอายุ"""
    try:
        # Get the member object of the logged-in user
        member = request.user.member

        # Get current date for expiration comparison
        current_date = timezone.now().date()

        # Get coupons where member matches the logged-in user's member
        coupons = Coupon.objects.filter(
            member=member,  # Filter by member
            collect=True,  # Only show collected coupons
            used=False,  # Exclude used coupons
            promotion__end__gte=current_date  # Only show unexpired coupons
        ).select_related(
            'promotion',
            'promotion__store'
        ).order_by('-collected_at')  # Optional: order by collection date

        context = {
            'coupons': coupons,
            'username': request.user.username
        }

        return render(request, 'my_coupons.html', context)

    except Member.DoesNotExist:
        messages.error(request, "ไม่พบข้อมูลสมาชิกในระบบ")
        return redirect('home')

def PromotionDetailsMember(request, store_id, promotion_id, coupon_id):
    promotion = get_object_or_404(Promotion, id=promotion_id, store_id=store_id)
    coupon = get_object_or_404(Coupon, id=coupon_id, promotion=promotion)
    stores = Store.objects.all()

    return render(request, 'PromotionDetailsMember.html', {
        'promotion': promotion,
        'coupon': coupon,
        'stores': stores,
    })

def PromotionDetailsStore(request, promotion_id, coupon_id):
    # ดึงข้อมูล Promotion และ Coupon ที่เกี่ยวข้อง
    promotion = get_object_or_404(Promotion, id=promotion_id)
    coupon = get_object_or_404(Coupon, id=coupon_id, promotion=promotion)

    return render(request, 'PromotionDetailsStore.html', {
        'promotion': promotion,
        'coupon': coupon,
    })

@login_required
def list_member_collect_coupons(request):
    store = get_object_or_404(Store, owner=request.user.member)

    # Get all coupons for all promotions of this store
    coupons = Coupon.objects.filter(
        promotion__store=store
    ).select_related(
        'promotion',
        'member',
        'member__user'
    ).order_by('promotion', 'promotion_count')

    # Calculate statistics
    total_coupons = coupons.count()
    collected_coupons = coupons.filter(collect=True).count()
    is_coupon_used = coupons.filter(used=True).count()
    used_coupons = coupons.filter(used=True).count()
    available_coupons = total_coupons - collected_coupons

    context = {
        'coupons': coupons,
        'total_coupons': total_coupons,
        'collected_coupons': collected_coupons,
        'used_coupons': used_coupons,
        'available_coupons': available_coupons,
        'is_coupon_used': is_coupon_used
    }

    return render(request, 'list_member_collect_coupons.html', context)


@login_required
def Completed_coupons(request):
    from django.utils import timezone
    current_date = timezone.now().date()

    current_member = request.user.member
    username = request.user.username

    scanned_qrcodes = ScannedQRCode.objects.all()

    coupons = (Coupon.objects
               .filter(
        id__in=scanned_qrcodes.values_list('scanned_text', flat=True),
        collect=True,
        used=False,
        member=current_member,
        promotion__start__lte=current_date,  # Promotion has started
        promotion__end__gte=current_date,  # Promotion hasn't ended
    )
               .select_related('promotion', 'promotion__store', 'member')
               .order_by('promotion'))

    promotion_counts = {}
    for coupon in coupons:
        promo_id = coupon.promotion.id
        if promo_id not in promotion_counts:
            promotion_counts[promo_id] = {
                'total_required': coupon.promotion.cups,
                'collected': 1,
                'coupons': [coupon]
            }
        else:
            promotion_counts[promo_id]['collected'] += 1
            promotion_counts[promo_id]['coupons'].append(coupon)

    completed_coupons = [
        {
            'coupon': promo_data['coupons'][0],
            'promotion_id': promo_data['coupons'][0].promotion.id,
            'collected_count': promo_data['collected'],
            'total_required': promo_data['total_required'],
            'is_complete': True
        }
        for promo_data in promotion_counts.values()
        if promo_data['collected'] >= promo_data['total_required']
    ]

    return render(request, 'completed_coupons.html', {
        'display_coupons': completed_coupons,
        'username': username,
    })

@login_required
def Pending_coupons(request):
    scanned_qrcodes = ScannedQRCode.objects.all()
    username = request.user.username

    coupons = (Coupon.objects
               .filter(
                   id__in=scanned_qrcodes.values_list('scanned_text', flat=True),
                   collect=True
               )
               .select_related('promotion', 'promotion__store', 'member')
               .order_by('promotion'))

    promotion_counts = {}
    for coupon in coupons:
        promo_id = coupon.promotion.id
        if promo_id not in promotion_counts:
            promotion_counts[promo_id] = {
                'total_required': coupon.promotion.cups,  # Changed from count to cups
                'collected': 1,
                'coupons': [coupon]
            }
        else:
            promotion_counts[promo_id]['collected'] += 1
            promotion_counts[promo_id]['coupons'].append(coupon)

    display_coupons = [
        {
            'coupon': promo_data['coupons'][0],
            'collected_count': promo_data['collected'],
            'total_required': promo_data['total_required'],
            'is_complete': False,
            'promotion_id': promo_data['coupons'][0].promotion.id
        }
        for promo_data in promotion_counts.values()
        if promo_data['collected'] < promo_data['total_required']
    ]

    return render(request, 'pending_coupons.html', {
        'display_coupons': display_coupons,
        'username': username
    })


@login_required
def verify_coupons(request, promotion_id):
    username = request.user.username
    member = request.user.member

    try:
        # Get promotion and ensure it exists
        promotion = get_object_or_404(Promotion, id=promotion_id)

        # Get collected coupons for this promotion
        collected_coupons = Coupon.objects.filter(
            promotion=promotion,
            member=member,
            collect=True,
            used=False  # Only count unused coupons
        ).select_related('promotion', 'promotion__store')

        # Get the required number of cups from promotion
        total_required = promotion.cups if promotion.cups else 0
        collected_count = collected_coupons.count()

        # Check if enough coupons are collected
        is_complete = collected_count >= total_required if total_required > 0 else False

        # Prepare display data
        display_data = {
            'promotion': promotion,
            'collected_count': collected_count,
            'total_required': total_required,
            'total_coupons': promotion.coupons.count(),
            'is_complete': is_complete,
            'coupons': collected_coupons,
        }

        # Add debugging information
        print(f"Promotion: {promotion.name}")
        print(f"Required cups: {total_required}")
        print(f"Collected count: {collected_count}")
        print(f"Is complete: {is_complete}")

        return render(request, 'verify_coupons.html', {
            'display_coupons': [display_data],
            'username': username,
        })

    except Promotion.DoesNotExist:
        messages.error(request, "ไม่พบโปรโมชั่นที่ระบุ")
        return redirect('my_coupons')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('my_coupons')

@login_required
def verify_pending_coupons(request, promotion_id):
    username = request.user.username
    member = request.user.member

    try:
        promotion = get_object_or_404(Promotion, id=promotion_id)
        collect_coupons = Coupon.objects.filter(
            promotion=promotion,
            member=member,
            collect=True
        ).select_related('promotion', 'promotion__store')

        total_required = promotion.cups
        collected_count = collect_coupons.count()
        remaining_count = total_required - collected_count

        display_data = {
            'promotion': promotion,
            'collected_count': collected_count,
            'total_required': total_required,
            'remaining_count': remaining_count,
            'coupons': collect_coupons,
        }

        return render(request, 'verify_pending_coupons.html', {
            'display_coupons': [display_data],
            'username': username,
        })

    except Promotion.DoesNotExist:
        messages.error(request, "ไม่มีโปรโมชั่นเพิ่มเติม")
        return redirect('my_coupons')

@login_required
def use_coupon(request, promotion_id):
    scanned_qrcodes = ScannedQRCode.objects.all()
    username = request.user.username

    # ดึงคูปองที่ตรงกับ promotion_id และมี collect=True
    coupons = (Coupon.objects
               .filter(
                   id__in=scanned_qrcodes.values_list('scanned_text', flat=True),
                   collect=True,
                   promotion_id=promotion_id
               )
               .select_related('promotion', 'promotion__store', 'member')
               .order_by('promotion_count'))

    if coupons.exists():
        promotion = coupons.first().promotion
        collected_count = coupons.count()
        is_completed = collected_count >= promotion.cups  # ใช้ cups เป็นเงื่อนไข

        # ดึง QR Code รูปแรกของโปรโมชั่น
        qr_code_image = coupons.first().use_qr_code_url_image.url if coupons.first().use_qr_code_url_image else None

        if is_completed:
            context = {
                'username': username,
                'promotion': promotion,
                'coupons': coupons,
                'collected_count': collected_count,
                'total_required': promotion.cups,
                'qr_code_image': qr_code_image  # ส่งพาธ QR Code ไปยังเทมเพลต
            }
            return render(request, 'use_coupon.html', context)
        else:
            messages.error(request, 'โปรโมชั่นนี้ยังสะสมไม่ครบ')
    else:
        messages.error(request, 'ไม่พบคูปองสำหรับโปรโมชั่นนี้')

    return redirect('completed_coupons')

@login_required
def confirm_coupon_use(request, store_id, promotion_id, coupon_id):
    try:
        store = get_object_or_404(Store, id=store_id)
        promotion = get_object_or_404(Promotion, id=promotion_id, store=store)
        coupon = get_object_or_404(Coupon, id=coupon_id, promotion=promotion)

        print(f"Debug: Processing coupon {coupon_id} for promotion {promotion_id}")
        print(f"Debug: Current used status: {coupon.used}")
        print(f"Debug: Current collect status: {coupon.collect}")

        collected_coupons = Coupon.objects.filter(
            promotion=promotion,
            member=coupon.member,
            collect=True
        )

        unused_collected_count = collected_coupons.filter(used=False).count()

        # ตรวจสอบสิทธิ์การใช้คูปอง
        validations = {
            'is_expired': promotion.end < timezone.now().date(),
            'is_collected': coupon.collect,
            'has_enough_coupons': unused_collected_count >= promotion.cups,
            'already_used': coupon.used,
            'is_store_owner': request.user.member == store.owner
        }

        # ตรวจสอบ Wallet ของลูกค้า
        customer_wallet = coupon.member.wallet if coupon.member else None
        store_wallet = store.owner.wallet  # กระเป๋าเงินของร้านค้า

        if promotion.free is None and promotion.discount is not None:
            # คำนวณราคาหลังหักส่วนลด
            discount_amount = (promotion.discount / 100) * promotion.price
            final_price = promotion.price - discount_amount
            validations['has_sufficient_funds'] = customer_wallet.balance >= final_price if customer_wallet else False
        else:
            validations['has_sufficient_funds'] = True  # ฟรี ไม่ต้องตรวจสอบเงิน

        context = {
            'store': store,
            'promotion': promotion,
            'coupon': coupon,
            'member': coupon.member if coupon.member else None,
            'collected_count': unused_collected_count,
            'required_count': promotion.cups,
            'validations': validations
        }

        if request.method == 'POST' and validations['is_store_owner']:
            if not coupon.used and validations['has_enough_coupons']:
                coupons_to_use = collected_coupons.filter(used=False)[:promotion.cups]

                # ✅ **ถ้าเป็นคูปองแบบฟรี → ไม่ต้องตัดเงิน**
                if promotion.free is not None:
                    final_price = Decimal('0.00')

                # ✅ **ถ้าเป็นคูปองแบบลดราคา → ตัดเงินตามส่วนลด**
                elif promotion.discount is not None:
                    discount_amount = (promotion.discount / 100) * promotion.price
                    final_price = promotion.price - discount_amount

                    # ตรวจสอบว่าลูกค้ามียอดเงินพอหรือไม่
                    if not customer_wallet or not customer_wallet.deduct_balance(final_price):
                        messages.error(request, "ยอดเงินไม่เพียงพอ")
                        return redirect('confirm_coupon_use', store_id=store_id,
                                        promotion_id=promotion_id, coupon_id=coupon_id)

                    # โอนเงินเข้ากระเป๋าของร้านค้า
                    store_wallet.add_balance(final_price)

                    # ✅ **บันทึกธุรกรรม**
                    Transaction.objects.create(
                        wallet=customer_wallet,
                        amount=final_price,
                        transaction_type='DEBIT',
                        description=f'ใช้คูปองสำหรับ {promotion.name}'
                    )
                    Transaction.objects.create(
                        wallet=store_wallet,
                        amount=final_price,
                        transaction_type='CREDIT',
                        description=f'รับเงินจาก {coupon.member.user.username} สำหรับ {promotion.name}'
                    )

                # ✅ **อัปเดตสถานะคูปอง**
                for coup in coupons_to_use:
                    coup.used = True
                    coup.used_at = timezone.now()
                    coup.save()
                    print(f"Debug: Marked coupon {coup.id} as used")

                messages.success(request, f"ใช้คูปองสำเร็จ! ใช้คูปองจำนวน {promotion.cups} ใบ")
                return redirect('promotions_store')

        return render(request, 'confirm_coupon_use.html', context)

    except Exception as e:
        print(f"Debug: Error occurred: {str(e)}")
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('promotions_store')

@login_required
def coupon_used_history(request):
    try:
        # Get the member object of the logged-in user
        member = request.user.member

        # Get coupons where member matches the logged-in user's member
        coupons = Coupon.objects.filter(
            member=member,  # Filter by member
            used=True  # Only show collected coupons
        ).select_related('promotion', 'promotion__store')  # Optimize queries

        context = {
            'coupons': coupons,
            'username': request.user.username
        }

        return render(request, 'coupon_used_history.html', context)

    except Member.DoesNotExist:
        messages.error(request, "ไม่พบข้อมูลสมาชิกในระบบ")
        return redirect('home')

@login_required
def list_customer_use_coupons(request):
    # Get the current member/user
    member = request.user.member

    # Get all collected coupons for this member
    coupons = Coupon.objects.filter(
        member=member,
        collect=True
    ).select_related(
        'promotion',
        'promotion__store'
    ).order_by('-collected_at')

    # Calculate statistics
    total_collected_coupons = coupons.count()
    used_coupons = coupons.filter(used=True).count()
    available_coupons = total_collected_coupons - used_coupons

    context = {
        'coupons': coupons,
        'total_collected_coupons': total_collected_coupons,
        'used_coupons': used_coupons,
        'available_coupons': available_coupons
    }

    return render(request, 'list_customer_use_coupons.html', context)

# ฟังก์ชันขอเป็นเจ้าของร้าน
@login_required
def request_store_ownership(request):
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        member = None

    # Check for any existing requests
    existing_requests = StoreOwnerRequest.objects.filter(user=request.user).exists()
    if existing_requests:
        messages.warning(request, "คุณเคยส่งคำขอไปแล้ว ไม่สามารถส่งคำขอซ้ำได้")
        return render(request, 'request_store_ownership.html', {'form': StoreOwnershipRequestForm()})

    if request.method == 'POST':
        form = StoreOwnershipRequestForm(request.POST)
        if form.is_valid():
            store_request = form.save(commit=False)
            store_request.user = request.user
            store_request.save()
            messages.success(request, "ส่งคำขอสำเร็จ! รอแอดมินตรวจสอบ")
            return redirect('request_store_ownership.html')
        else:
            messages.error(request, "กรุณากรอกข้อมูลให้ถูกต้อง")
    else:
        form = StoreOwnershipRequestForm()

    return render(request, 'request_store_ownership.html', {'form': form})

# ฟังก์ชันสำหรับแอดมินดูคำขอ
@login_required
def admin_store_requests(request):
    if not request.user.is_staff:
        messages.error(request, "คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        return redirect('home')

    requests = StoreOwnerRequest.objects.filter(status="pending")
    return render(request, 'admin_store_requests.html', {'requests': requests})

# ฟังก์ชันดูรายละเอียดคำขอ
@login_required
def store_request_detail(request, request_id):
    if not request.user.is_staff:
        messages.error(request, "คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        return redirect('home')

    shop_request = get_object_or_404(StoreOwnerRequest, id=request_id)
    return render(request, 'store_request_detail.html', {'store_request': shop_request})

# ฟังก์ชันอนุมัติคำขอและสร้างร้านค้า
@login_required
def approve_store_request(request, request_id):
    if not request.user.is_staff:
        messages.error(request, "คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        return redirect('home')

    shop_request = get_object_or_404(StoreOwnerRequest, id=request_id)

    # ค้นหา Member ที่เกี่ยวข้องกับ User
    member, created = Member.objects.get_or_create(user=shop_request.user)
    print(f"Member ที่พบ: {member}, created: {created}")  # Debug

    # ตรวจสอบว่าร้านนี้เคยถูกสร้างไปแล้วหรือไม่
    existing_store = Store.objects.filter(store_name=shop_request.shop_name, owner=member).exists()
    if existing_store:
        messages.warning(request, f"ร้าน {shop_request.shop_name} ถูกสร้างไปแล้ว")
        return redirect('admin_store_requests')

    # สร้างร้านใหม่
    new_store = Store.objects.create(store_name=shop_request.shop_name, owner=member)

    # อัปเดตสถานะคำขอเป็น "อนุมัติแล้ว"
    shop_request.status = "approved"
    shop_request.approved_at = now()
    shop_request.approved_by = request.user  # ระบุว่าใครอนุมัติ
    shop_request.save()

    # อัปเดต `is_owner` เป็น True ใน `Member`
    member.is_owner = True
    member.save()

    messages.success(request, f"อนุมัติคำขอ และสร้างร้าน {new_store.store_name} สำเร็จ!<br>"
                              f"ผู้ใช้ {shop_request.user.username} เป็นเจ้าของร้านแล้ว")
    return redirect('admin_store_requests')

def approved_store_owners(request):
    approved_requests = StoreOwnerRequest.objects.filter(status='approved').select_related('user', 'approved_by')

    context = {
        'approved_requests': approved_requests
    }
    return render(request, 'approved_owners_list.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_store_management(request):
    # ดึงข้อมูลร้านค้าที่เจ้าของมี is_owner = True
    stores = Store.objects.select_related(
        'owner',
        'owner__user'
    ).prefetch_related(
        'promotions',
        'promotions__coupons'
    ).filter(
        owner__is_owner=True
    )

    # นับจำนวนร้านค้าทั้งหมด
    total_stores = stores.count()

    # นับจำนวนโปรโมชันทั้งหมดเฉพาะจากร้านที่ is_owner = True
    total_promotions = Promotion.objects.filter(
        store__owner__is_owner=True
    ).count()

    # นับจำนวนคูปองทั้งหมดเฉพาะจากร้านที่ is_owner = True
    total_coupons = Coupon.objects.filter(
        promotion__store__owner__is_owner=True
    ).count()

    # คำนวณสถิติคูปองสำหรับแต่ละร้าน
    stores = stores.annotate(
        total_coupons=Count('promotions__coupons'),
        uncollected_coupons=Count(
            'promotions__coupons',
            filter=Q(promotions__coupons__collect=False)
        ),
        collected_coupons=Count(
            'promotions__coupons',
            filter=Q(promotions__coupons__collect=True, promotions__coupons__used=False)
        ),
        used_coupons=Count(
            'promotions__coupons',
            filter=Q(promotions__coupons__used=True)
        )
    )

    context = {
        'stores': stores,
        'total_stores': total_stores,
        'total_promotions': total_promotions,
        'total_coupons': total_coupons,
        'page_title': 'Store Management',
    }

    return render(request, 'admin_store_management.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_store(request, store_id):
    if request.method == 'POST':
        store = get_object_or_404(Store, id=store_id)
        try:
            store_name = store.store_name
            store.delete()
            messages.success(request, f'ลบร้านค้า {store_name} เรียบร้อยแล้ว')
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาดในการลบร้านค้า: {str(e)}')
    return redirect('admin_store_management')


@login_required
@user_passes_test(lambda u: u.is_staff)
def store_detail(request, store_id):
    store = get_object_or_404(Store.objects.select_related(
        'owner',
        'owner__user'
    ).prefetch_related(
        'promotions',
        'promotions__coupons'
    ), id=store_id)

    # รวมข้อมูลสถิติของร้าน
    store_stats = {
        'total_promotions': store.promotions.count(),
        'total_coupons': sum(p.coupons.count() for p in store.promotions.all()),
        'active_promotions': store.promotions.filter(end__gte=timezone.now()).count()
    }

    context = {
        'store': store,
        'stats': store_stats,
    }

    return render(request, 'store_detail.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_member_management(request):
    # ดึงข้อมูลสมาชิกทั้งหมด
    members = Member.objects.select_related('user').annotate(
        is_admin=Case(
            When(user__is_staff=True, then=True),
            default=False,
            output_field=BooleanField()
        ),
        date_joined=F('user__date_joined')  # วันที่สมัคร
    )

    # คำนวณจำนวนสมาชิก
    total_members = members.count()
    total_owners = members.filter(is_owner=True).count()
    total_non_owners = total_members - total_owners
    total_admins = User.objects.filter(is_staff=True).count()

    context = {
        'members': members,
        'total_members': total_members,
        'total_owners': total_owners,
        'total_non_owners': total_non_owners,
        'total_admins': total_admins,
        'page_title': 'Member Management',
    }

    return render(request, 'admin_member_management.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def member_detail(request, member_id):
    member = get_object_or_404(Member.objects.select_related(
        'user'
    ).prefetch_related(
        'stores',
        'stores__promotions',
        'stores__promotions__coupons'
    ), id=member_id)

    # รวมข้อมูลสถิติของสมาชิก
    member_stats = {
        'total_stores': member.stores.count(),
        'total_promotions': sum(s.promotions.count() for s in member.stores.all()),
        'total_coupons': sum(
            p.coupons.count()
            for s in member.stores.all()
            for p in s.promotions.all()
        ),
        'active_promotions': member.stores.filter(
            promotions__end__gte=timezone.now()
        ).distinct().count()
    }

    context = {
        'member': member,
        'stats': member_stats,
    }

    return render(request, 'member_detail.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def update_member_name(request, member_id):
    member = get_object_or_404(Member.objects.select_related('user'), id=member_id)
    user = member.user

    if request.method == 'POST':
        form = MemberUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'อัปเดตชื่อสมาชิกเรียบร้อยแล้ว!')
            return redirect('admin_member_management')
        else:
            messages.error(request, 'เกิดข้อผิดพลาดในการอัปเดตชื่อสมาชิก')

    else:
        form = MemberUpdateForm(instance=user)

    context = {
        'form': form,
        'member': member,
    }
    return render(request, 'update_member_name.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_member(request, member_id):
    if request.method == 'POST':
        member = get_object_or_404(Member, id=member_id)
        try:
            user_name = f"{member.user.first_name} {member.user.last_name}"
            member.user.delete()  # This will cascade delete the UserProfile
            messages.success(request, f'ลบสมาชิก {user_name} เรียบร้อยแล้ว')
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาดในการลบสมาชิก: {str(e)}')
    return redirect('admin_member_management')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_coupon_management(request):

    # คำนวณสถิติ
    total_coupons = Coupon.objects.count()  # คูปองทั้งหมด
    used_coupons = Coupon.objects.filter(used=True).count()  # คูปองที่ถูกใช้แล้ว
    unused_coupons = Coupon.objects.filter(used=False).count()  # คูปองที่ยังไม่ได้ใช้
    total_promotions = Promotion.objects.count()  # โปรโมชั่นทั้งหมด

    # รายการคูปอง (ดึงข้อมูลร้านค้าผ่าน Promotion)
    coupons = Coupon.objects.select_related('promotion__store', 'member').order_by('-collected_at')

    context = {
        'coupons': coupons,
        'total_coupons': total_coupons,
        'used_coupons': used_coupons,
        'unused_coupons': unused_coupons,
        'total_promotions': total_promotions,
        'page_title': 'จัดการคูปอง',
    }
    return render(request, 'admin_coupon_management.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def coupon_detail(request, coupon_id):
    """ ดูรายละเอียดคูปอง """
    coupon = get_object_or_404(Coupon.objects.select_related('promotion', 'member'), id=coupon_id)

    context = {
        'coupon': coupon,
        'page_title': 'รายละเอียดคูปอง',
    }
    return render(request, 'coupon_detail.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_coupon(request, coupon_id):
    """ ลบคูปอง """
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        coupon.delete()
        messages.success(request, 'ลบคูปองเรียบร้อยแล้ว!')
        return redirect('admin_coupon_management')

    return render(request, 'confirm_delete.html', {'object': coupon, 'page_title': 'ยืนยันการลบคูปอง'})

@login_required
def expired_coupons(request):
    """แสดงรายการคูปองที่หมดอายุของผู้ใช้"""
    try:
        # Get the member object of the logged-in user
        member = request.user.member

        # Get current date for comparison
        current_date = date.today()

        # Get expired coupons where member matches the logged-in user's member
        coupons = Coupon.objects.filter(
            member=member,  # Filter by member
            collect=True,  # Only show collected coupons
            used=False,  # Exclude used coupons
            promotion__end__lt=current_date  # Filter for expired promotions
        ).select_related(
            'promotion',
            'promotion__store'
        ).order_by('-collected_at')

        context = {
            'coupons': coupons,
            'username': request.user.username
        }

        return render(request, 'expired_coupons.html', context)

    except Member.DoesNotExist:
        messages.error(request, "ไม่พบข้อมูลสมาชิกในระบบ")
        return redirect('home')

@login_required
def my_wallet(request):
    """หน้ากระเป๋าเงินของฉัน - แสดงยอดเงินและสรุปการใช้งาน"""
    member = request.user.member
    wallet, created = Wallet.objects.get_or_create(member=member)

    # คำนวณสถิติการใช้งานวันนี้
    today_transactions = wallet.transactions.filter(
        created_at__date=timezone.now().date()
    )
    today_spent = today_transactions.filter(
        transaction_type='DEBIT'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    today_received = today_transactions.filter(
        transaction_type='CREDIT'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    # รายการล่าสุด 5 รายการ
    recent_transactions = wallet.transactions.all()[:5]

    context = {
        'wallet': wallet,
        'today_spent': today_spent,
        'today_received': today_received,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'my_wallet.html', context)

@login_required
def top_up(request):
    """หน้าเติมเงิน"""
    wallet = request.user.member.wallet

    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
            if amount <= 0:
                messages.error(request, 'กรุณาระบุจำนวนเงินที่มากกว่า 0')
                return redirect('wallet_top_up')

            wallet.add_balance(amount)
            Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type='CREDIT',
                description=request.POST.get('description', 'เติมเงิน')
            )
            messages.success(request, f'เติมเงินสำเร็จ {amount:,.2f} บาท')
            return redirect('my_wallet')
        except (ValueError, TypeError):
            messages.error(request, 'จำนวนเงินไม่ถูกต้อง')

    context = {
        'wallet': wallet
    }
    return render(request, 'wallet_top_up.html', context)

@login_required
def show_card(request):
    """หน้าแสดงเลขบัตรและข้อมูลกระเป๋าเงิน"""
    member = request.user.member

    # สร้างเลขบัตรถ้ายังไม่มี
    if not member.card_number:
        member.save()

    # ดึงข้อมูลกระเป๋าเงิน
    wallet, created = Wallet.objects.get_or_create(member=member)

    # คำนวณสถิติการใช้งานวันนี้
    today_transactions = wallet.transactions.filter(
        created_at__date=timezone.now().date()
    )
    today_spent = today_transactions.filter(
        transaction_type='DEBIT'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    today_received = today_transactions.filter(
        transaction_type='CREDIT'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    # รายการล่าสุด 5 รายการ
    recent_transactions = wallet.transactions.all()[:5]

    context = {
        'member': member,
        'card_number': member.card_number,
        'username': member.user.username,
        'balance': wallet.balance,
        'today_spent': today_spent,
        'today_received': today_received,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'wallet_show_card.html', context)

@login_required
def transfer(request):
    """หน้าโอนเงิน"""
    wallet = request.user.member.wallet

    if request.method == 'POST':
        try:
            recipient_card = request.POST.get('card_number')
            amount = Decimal(request.POST.get('amount', '0'))
            description = request.POST.get('description', 'โอนเงิน')

            if amount <= 0:
                messages.error(request, 'จำนวนเงินต้องมากกว่า 0')
                return redirect('wallet_transfer')

            try:
                recipient = Member.objects.get(card_number=recipient_card)
            except Member.DoesNotExist:
                messages.error(request, 'ไม่พบเลขบัตรนี้ในระบบ')
                return redirect('wallet_transfer')

            if recipient == request.user.member:
                messages.error(request, 'ไม่สามารถโอนเงินให้ตัวเองได้')
                return redirect('wallet_transfer')

            if wallet.balance < amount:
                messages.error(request, 'ยอดเงินคงเหลือไม่เพียงพอ')
                return redirect('wallet_transfer')

            with transaction.atomic():
                wallet.deduct_balance(amount)
                recipient.wallet.add_balance(amount)

                Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='DEBIT',
                    description=f'โอนเงินให้ {recipient.user.username} - {description}'
                )

                Transaction.objects.create(
                    wallet=recipient.wallet,
                    amount=amount,
                    transaction_type='CREDIT',
                    description=f'รับโอนจาก {request.user.username} - {description}'
                )

            messages.success(request, f'โอนเงินจำนวน ฿{amount:,.2f} ให้ {recipient.user.username} สำเร็จ')
            return redirect('my_wallet')

        except ValueError:
            messages.error(request, 'จำนวนเงินไม่ถูกต้อง')
        except Exception as e:
            messages.error(request, 'เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง')

    context = {
        'wallet': wallet
    }
    return render(request, 'wallet_transfer.html', context)

@login_required
def transaction_history(request):
    """หน้าประวัติการทำรายการ"""
    wallet = request.user.member.wallet
    transactions = wallet.transactions.all()

    # คำนวณสรุปยอด
    summary = {
        'total_credit': transactions.filter(
            transaction_type='CREDIT'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0'),

        'total_debit': transactions.filter(
            transaction_type='DEBIT'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0'),

        # เพิ่มสถิติรายเดือนนี้
        'month_credit': transactions.filter(
            transaction_type='CREDIT',
            created_at__month=timezone.now().month
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0'),

        'month_debit': transactions.filter(
            transaction_type='DEBIT',
            created_at__month=timezone.now().month
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0'),
    }

    context = {
        'transactions': transactions,
        'summary': summary,
    }
    return render(request, 'wallet_history.html', context)

def financial_dashboard(request):
    # Get current month
    today = timezone.now()
    current_month = today.month
    current_year = today.year

    # Calculate totals
    total_credit = Transaction.objects.filter(
        transaction_type='credit'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_debit = Transaction.objects.filter(
        transaction_type='debit'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # Calculate monthly totals
    month_credit = Transaction.objects.filter(
        transaction_type='credit',
        date__month=current_month,
        date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    month_debit = Transaction.objects.filter(
        transaction_type='debit',
        date__month=current_month,
        date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # Prepare context
    context = {
        'summary': {
            'total_credit': total_credit,
            'total_debit': total_debit,
            'month_credit': month_credit,
            'month_debit': month_debit,
        }
    }

    return render(request, 'wallet_history.html', context)
