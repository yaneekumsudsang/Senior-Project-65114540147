from .models import *
from django.contrib.auth.models import User
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm
from .models import Member
from django.shortcuts import render, get_object_or_404
from .models import Promotion

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

#@login_required
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
    return redirect('koupon')

@login_required
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

def scan_qr(request):
    return render(request, 'scan_qr.html')
