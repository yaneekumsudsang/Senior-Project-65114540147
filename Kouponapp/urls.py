from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.promotions_view, name="koupon"),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('koupon_logout/', views.koupon_logout, name='koupon_logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('scan_qr/', views.scan_qr, name='scan_qr'),
]
