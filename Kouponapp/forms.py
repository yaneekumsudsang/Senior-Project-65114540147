from django import forms
from django.contrib.auth.models import User
from .models import *
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class RegisterForm(forms.Form):
    username = forms.CharField(label="ชื่อผู้ใช้",
                               max_length=150,
                               widget=forms.TextInput(attrs={
                                   'placeholder': 'ชื่อผู้ใช้',
    }))
    first_name = forms.CharField(label="ชื่อ",
                                 max_length=30,
                                 widget=forms.TextInput(attrs={
                                     'placeholder': 'ชื่อ',
    }))
    last_name = forms.CharField(label="นามสกุล",
                                max_length=30,
                                widget=forms.TextInput(attrs={
                                    'placeholder': 'นามสกุล',
    }))
    phone = forms.CharField(label="เบอร์โทรศัพท์",
                            max_length=15,
                            widget=forms.TextInput(attrs={
                                'placeholder': 'เบอร์โทรศัพท์',
    }))
    email = forms.EmailField(label="อีเมล",
                             widget=forms.EmailInput(attrs={
                                 'placeholder': 'อีเมล',
    }))
    password = forms.CharField(label="รหัสผ่าน",
                               widget=forms.PasswordInput(attrs={
                                   'placeholder': 'รหัสผ่าน',
    }))
    confirm_password = forms.CharField(label="ยืนยันรหัสผ่าน",
                                       widget=forms.PasswordInput(attrs={
                                           'placeholder': 'ยืนยันรหัสผ่าน',
    }))

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError('รหัสผ่านไม่ตรงกัน')
        return confirm_password

class LoginForm(forms.Form):
    username = forms.CharField(
        label="ชื่อผู้ใช้งาน",
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'ชื่อผู้ใช้งาน',
        })
    )
    password = forms.CharField(
        label="รหัสผ่าน",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'รหัสผ่าน',
        })
    )


class ProfileForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded-lg bg-white',
            'placeholder': 'เบอร์โทรศัพท์'
        })
    )
    profile_img = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
        })
    )
    store_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded-lg bg-white',
            'placeholder': 'ชื่อร้าน'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        member = kwargs.pop('member', None)
        store = kwargs.pop('store', None)
        super().__init__(*args, **kwargs)

        if member:
            self.fields['phone'].initial = member.phone
            self.fields['profile_img'].initial = member.profile_img

        if store:
            self.fields['store_name'].initial = store.store_name
        else:
            # ถ้าไม่มีร้าน ซ่อนฟิลด์ชื่อร้าน
            self.fields['store_name'].widget = forms.HiddenInput()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class PromotionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        member = kwargs.pop('user', None)  # รับข้อมูล Member จาก view
        super().__init__(*args, **kwargs)
        if member:
            self.fields['store'].queryset = Store.objects.filter(owner=member)  # กรองร้านค้าเฉพาะของ Member

    coupon_count = forms.IntegerField(
        label="จำนวนคูปอง",
        required=False,
        initial=1,
        validators=[MinValueValidator(1)],
    )

    price = forms.DecimalField(
        label="ราคา",
        max_digits=10,
        decimal_places=2,
        required=True,  # บังคับกรอก
        validators=[MinValueValidator(0)],  # ค่าต่ำสุดคือ 0
    )

    class Meta:
        model = Promotion
        fields = ['picture', 'cupsize', 'cups', 'discount', 'free', 'name', 'details', 'start', 'end', 'coupon_count','price']
        widgets = {
            'start': forms.DateInput(attrs={'type': 'date'}),
            'end': forms.DateInput(attrs={'type': 'date'}),
            'details': forms.Textarea(attrs={
                'placeholder': 'กรุณากรอกรายละเอียดโปรโมชั่น',
                'rows': 3,
            }),
        }
        labels = {
            'picture': 'รูปภาพ',
            'cupsize': 'ขนาดแก้ว',
            'cups': 'จำนวนแก้วที่สะสม',
            'discount': 'ส่วนลด (%)',
            'free': 'จำนวนแก้วฟรี',
            'name': 'ชื่อโปรโมชั่น',
            'details': 'รายละเอียดโปรโมชั่น',
            'start': 'วันที่เริ่มใช้งาน',
            'end': 'วันหมดอายุ',
            'count': 'จำนวนคูปอง',
            'price': 'ราคา',

        }

    # ฟิลด์จำนวนแก้วที่สะสม
    cups = forms.IntegerField(
        label="จำนวนแก้วที่สะสม",
        validators=[MinValueValidator(0)],  # ค่าต่ำสุดคือ 0
    )

    # ฟิลด์ส่วนลด
    discount = forms.DecimalField(
        label="ส่วนลด (%)",
        max_digits=5,
        decimal_places=2,
        required=False,  # ไม่บังคับกรอก
        validators=[
            MinValueValidator(0),  # ค่าต่ำสุดคือ 0%
            MaxValueValidator(100),  # ค่าสูงสุดคือ 100%
        ],
    )

    # ฟิลด์จำนวนแก้วฟรี
    free = forms.IntegerField(
        label="จำนวนแก้วฟรี",
        required=False,  # ไม่บังคับกรอก
        validators=[MinValueValidator(0)],  # ค่าต่ำสุดคือ 0
    )
    # ตรวจสอบและตั้งค่า default ในฟิลด์ discount และ free

    count = forms.IntegerField(
        label="จำนวนคูปอง",
        required=False,
        initial=1,
        validators=[MinValueValidator(1)],  # ค่าต่ำสุดคือ 1
    )

    def clean(self):
        cleaned_data = super().clean()
        discount = cleaned_data.get('discount')
        free = cleaned_data.get('free')

        if discount and free:
            raise forms.ValidationError("ไม่สามารถระบุทั้งส่วนลดและจำนวนแก้วฟรีได้")

        if not discount and not free:
            raise forms.ValidationError("กรุณาระบุอย่างใดอย่างหนึ่ง: ส่วนลดหรือจำนวนแก้วฟรี")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # นำค่าจาก coupon_count ไปใส่ในฟิลด์ count ของโมเดล Promotion
        instance.count = self.cleaned_data.get('coupon_count', 1)
        if commit:
            instance.save()
        return instance

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['promotion', 'promotion_count', 'collect', 'collect_qr_code_url']

class MemberUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class StoreOwnershipRequestForm(forms.ModelForm):
    class Meta:
        model = StoreOwnerRequest
        fields = ['shop_name']
        labels = {
            'shop_name': 'ชื่อร้าน'
        }
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg bg-white',
                                                'placeholder': 'กรอกชื่อร้าน'})
        }
