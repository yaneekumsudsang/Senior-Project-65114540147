from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.Form):
    username = forms.CharField(label="ชื่อผู้ใช้", max_length=150, widget=forms.TextInput(attrs={
        'class': 'w-full p-2 border border-[#164863] rounded-2xl',
        'placeholder': 'ชื่อผู้ใช้',
    }))
    first_name = forms.CharField(label="ชื่อ", max_length=30, widget=forms.TextInput(attrs={
        'class': 'w-full p-2 border border-[#164863] rounded-2xl',
        'placeholder': 'ชื่อ',
    }))
    last_name = forms.CharField(label="นามสกุล", max_length=30, widget=forms.TextInput(attrs={
        'class': 'w-full p-2 border border-[#164863] rounded-2xl',
        'placeholder': 'นามสกุล',
    }))
    phone = forms.CharField(label="เบอร์โทรศัพท์", max_length=15, widget=forms.TextInput(attrs={
        'class': 'w-full p-2 border border-[#164863] rounded-2xl',
        'placeholder': 'เบอร์โทรศัพท์',
    }))
    email = forms.EmailField(label="อีเมล", widget=forms.EmailInput(attrs={
        'class': 'w-full p-2 border border-[#164863] rounded-2xl',
        'placeholder': 'อีเมล',
    }))
    password = forms.CharField(label="รหัสผ่าน", widget=forms.PasswordInput(attrs={
        'class': 'w-full p-2 border border-[#164863] rounded-2xl',
        'placeholder': 'รหัสผ่าน',
    }))
    confirm_password = forms.CharField(label="ยืนยันรหัสผ่าน", widget=forms.PasswordInput(attrs={
        'class': 'w-full p-2 border border-[#164863] rounded-2xl',
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
            'class': 'w-full p-2 border border-[#164863] rounded-2xl',
            'placeholder': 'ชื่อผู้ใช้งาน',
        })
    )
    password = forms.CharField(
        label="รหัสผ่าน",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-2 border border-[#164863] rounded-2xl',
            'placeholder': 'รหัสผ่าน',
        })
    )
class ProfileForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-60 p-2 border border-gray-300 rounded-lg',
            'placeholder': 'เบอร์โทรศัพท์'
        })
    )
    profile_img = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']  # ฟิลด์จาก User

    def __init__(self, *args, **kwargs):
        member = kwargs.pop('member', None)  # รับ instance ของ Member ผ่าน kwargs
        super().__init__(*args, **kwargs)
        if member:
            self.fields['phone'].initial = member.phone  # ตั้งค่าเบอร์โทรเริ่มต้น
            self.fields['profile_img'].initial = member.profile_img  # ตั้งค่ารูปโปรไฟล์เริ่มต้น
