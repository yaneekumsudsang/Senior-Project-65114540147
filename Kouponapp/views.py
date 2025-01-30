# Standard library imports
import logging
import os
import io
import base64
from datetime import timezone, timedelta

# Third-party imports
import numpy as np
import cv2
from pyzbar.pyzbar import decode
import segno
from qr_code.qrcode.utils import QRCodeOptions

# Django built-in imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.models import Count, Sum, Q
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.cache import never_cache

# Local app imports
from .forms import RegisterForm, LoginForm, ProfileForm, PromotionForm
from .models import Member, Store, Promotion, Coupon, ScannedQRCode, StoreOwnerRequest

def promotions_view(request):
    data = Promotion.objects.all()[:5]
    return render(request, 'home.html', {'data':data})

def promotions_all(request):
    all_promotions = Promotion.objects.all()  # ดึงข้อมูลโปรโมชั่นทั้งหมด
    return render(request, 'promotions_all.html', {'all_promotions': all_promotions})

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
                    return redirect('admin_store_requests')

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

        # เพิ่มการเช็คสถานะคำขอ
        pending_request = StoreOwnerRequest.objects.filter(
            user=request.user,
            status='pending'
        ).exists()

        context = {
            'user': request.user,
            'pending_request': pending_request,
        }

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

        # ดึงข้อมูลคูปองที่ถูกใช้และนับจำนวนคูปองที่ถูกใช้ในแต่ละโปรโมชั่น (เฉพาะร้านของเจ้าของ)
        used_coupons_by_promotion = Coupon.objects.filter(
            used=True,  # คูปองที่ถูกใช้แล้ว
            promotion__store=store  # คูปองที่ถูกใช้ในร้านของเจ้าของ
        ).values(
            'promotion__name'  # ชื่อของโปรโมชั่น (ดึงจาก Promotion)
        ).annotate(
            total_used=Count('id')  # นับจำนวนคูปองที่ถูกใช้
        )

        # สร้าง dictionary เพื่อเก็บข้อมูลโปรโมชั่นและจำนวนคูปองที่ถูกใช้
        promotion_data = {item['promotion__name']: item['total_used'] for item in used_coupons_by_promotion}
    else:
        promotions = []
        promotion_data = {}

    # ส่งข้อมูลโปรโมชันและข้อมูลกราฟไปยังเทมเพลต
    return render(request, 'promotions_store.html', {
        'promotions': promotions,
        'promotion_data': promotion_data  # ส่งข้อมูลโปรโมชั่นและจำนวนคูปองที่ถูกใช้ไปยังเทมเพลต
    })

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

@login_required
def Collect_coupons(request, store_id, promotion_id, coupon_id, timezone):
    """ฟังก์ชันสำหรับการสแกน QR Code และเก็บคูปอง"""
    try:
        current_member = Member.objects.get(user=request.user)

        # ดึงข้อมูลร้านค้า, โปรโมชั่น และคูปอง
        store = Store.objects.get(pk=store_id)
        promotion = Promotion.objects.get(id=promotion_id, store=store)
        coupon = Coupon.objects.get(id=coupon_id, promotion=promotion)

        # บันทึกการสแกน QR Code
        scanned_qr = ScannedQRCode.objects.create(
            scanned_text=str(coupon.id),
            is_url=False,
        )

        if coupon.collect:
            if coupon.member:
                messages.error(request, f"คูปองนี้ถูกสะสมไปแล้วโดย {coupon.member.user.username}")
            else:
                messages.error(request, "คูปองนี้ถูกสะสมไปแล้ว")
        elif promotion.end < timezone.now().date():
            messages.error(request, "คูปองนี้หมดอายุแล้ว")
        else:
            # อัปเดตสถานะคูปอง
            coupon.collect = True
            coupon.collected_at = timezone.now()
            coupon.member = current_member
            coupon.save()

            messages.success(request, f"คูปองถูกสะสมเรียบร้อยแล้วโดย {request.user.username}!")

    except Member.DoesNotExist:
        messages.error(request, "ไม่พบข้อมูลสมาชิกในระบบ")
    except Store.DoesNotExist:
        messages.error(request, "ไม่พบร้านค้านี้ในระบบ")
    except Promotion.DoesNotExist:
        messages.error(request, "ไม่พบโปรโมชั่นนี้ในระบบ")
    except Coupon.DoesNotExist:
        messages.error(request, "ไม่พบคูปองนี้ในระบบ")

    return redirect('my_coupons')

@login_required
def my_coupons(request):
    """แสดงรายการคูปองที่ผู้ใช้สะสม"""
    try:
        # Get the member object of the logged-in user
        member = request.user.member

        # Get coupons where member matches the logged-in user's member
        coupons = Coupon.objects.filter(
            member=member,  # Filter by member
            collect=True,  # Only show collected coupons
            used=False  # Exclude used coupons
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
    current_member = request.user.member
    username = request.user.username

    scanned_qrcodes = ScannedQRCode.objects.all()

    coupons = (Coupon.objects
               .filter(
        id__in=scanned_qrcodes.values_list('scanned_text', flat=True),
        collect=True,
        used=False,
        member=current_member
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
        promotion = get_object_or_404(Promotion, id=promotion_id)
        collected_coupons = Coupon.objects.filter(
            promotion=promotion,
            member=member,
            collect=True
        ).select_related('promotion', 'promotion__store')

        total_required = promotion.cups  # Changed from count to cups
        collected_count = collected_coupons.count()
        is_complete = collected_count >= total_required

        display_data = {
            'promotion': promotion,
            'collected_count': collected_count,
            'total_required': total_required,
            'total_coupons': promotion.coupon_set.count(),
            'is_complete': is_complete,
            'coupons': collected_coupons,
        }

        return render(request, 'verify_coupons.html', {
            'display_coupons': [display_data],
            'username': username,
        })

    except Promotion.DoesNotExist:
        messages.error(request, "ไม่พบโปรโมชั่นที่ระบุ")
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
       is_completed = collected_count >= promotion.cups  # Changed from count to cups

       if is_completed:
           context = {
               'username': username,
               'promotion': promotion,
               'coupons': coupons,
               'collected_count': collected_count,
               'total_required': promotion.cups  # Changed from count to cups
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

       validations = {
           'is_expired': promotion.end < now().date(),
           'is_collected': coupon.collect,
           'has_enough_coupons': unused_collected_count >= promotion.cups,  # Changed from count to cups
           'already_used': coupon.used,
           'is_store_owner': request.user.member == store.owner
       }

       context = {
           'store': store,
           'promotion': promotion,
           'coupon': coupon,
           'member': coupon.member if coupon.member else None,
           'collected_count': unused_collected_count,
           'required_count': promotion.cups,  # Changed from count to cups
           'validations': validations
       }

       if request.method == 'POST' and validations['is_store_owner']:
           if not coupon.used and validations['has_enough_coupons']:
               coupons_to_use = collected_coupons.filter(used=False)[:promotion.cups]  # Changed from count to cups

               for coup in coupons_to_use:
                   coup.used = True
                   coup.used_at = timezone.now()
                   coup.save()
                   print(f"Debug: Marked coupon {coup.id} as used")

               messages.success(request, f"ใช้คูปองสำเร็จ! ใช้คูปองจำนวน {promotion.cups} ใบ")  # Changed from count to cups
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
    if request.method == 'POST':
        shop_name = request.POST.get('store_name')
        if not shop_name:
            messages.error(request, "กรุณากรอกชื่อร้าน")
            return redirect('request_store')

        # ตรวจสอบว่าผู้ใช้มีคำขอที่ยังไม่อนุมัติหรือไม่
        existing_request = StoreOwnerRequest.objects.filter(user=request.user, status="pending").exists()
        if existing_request:
            messages.warning(request, "คุณได้ส่งคำขอไปแล้ว กรุณารอการตรวจสอบ")
            return redirect('request_store')

        # สร้างคำขอใหม่
        StoreOwnerRequest.objects.create(user=request.user, shop_name=shop_name)
        messages.success(request, "ส่งคำขอสำเร็จ! รอแอดมินตรวจสอบ")
        return redirect('request_store')

    return render(request, 'profile.html')

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
        return redirect('admin_store_requests')

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

    messages.success(request, f"อนุมัติคำขอ และสร้างร้าน {new_store.store_name} สำเร็จ! ผู้ใช้ {shop_request.user.username} เป็นเจ้าของร้านแล้ว")
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
    # Get all stores with related data
    stores = Store.objects.select_related(
        'owner',
        'owner__user'
    ).prefetch_related(
        'promotions'
    ).all()

    # Calculate statistics
    total_stores = stores.count()
    total_promotions = Promotion.objects.count()
    total_coupons = Coupon.objects.count()

    # Add total_coupons to each store
    for store in stores:
        store.total_coupons = Coupon.objects.filter(promotion__store=store).count()

    context = {
        'stores': stores,
        'total_stores': total_stores,
        'total_promotions': total_promotions,
        'total_coupons': total_coupons,
    }

    return render(request, 'admin_store_management.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_store(request, store_id):
    if request.method == 'POST':
        store = get_object_or_404(Store, id=store_id)
        store.delete()
        messages.success(request, f'ลบร้านค้า {store.store_name} เรียบร้อยแล้ว')
        return redirect('admin_store_management')
    return redirect('admin_store_management')