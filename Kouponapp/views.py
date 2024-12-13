from .models import *
from django.contrib.auth.models import User
from .forms import RegisterForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import LoginForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import EditProfileForm
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm


def promotions_view(request):
    data = Promotion.objects.all()
    return render(request, 'home.html', {'data':data})

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
                return redirect('koupon')  # Redirect to the home page
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
    return redirect('koupon')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = Member(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขข้อมูลสำเร็จแล้ว')
            return redirect('profile')  # เปลี่ยนเส้นทางไปยังหน้าข้อมูลสมาชิก
        else:
            messages.error(request, 'มีข้อผิดพลาด กรุณาตรวจสอบข้อมูลอีกครั้ง')
    else:
        form = Member(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})