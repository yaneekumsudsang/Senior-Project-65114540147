from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # หน้าแรกและ Authentication
    path("", views.promotions_view, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.koupon_logout, name="koupon_logout"),

    # โปรไฟล์สมาชิก
    path("profile/", views.profile_view, name="profile"),

    # การแสดงโปรโมชั่น
    path("promotions/member/", views.promotions_member, name="promotions_member"),
    path("promotions/all/", views.promotions_all, name="promotions_all"),
    path("promotions/", views.promotion_list, name="promotion_list"),
    path("promotion/<int:id>/", views.PromotionDetails, name="promotion_details"),

    # คูปองที่ใช้แล้ว
    path("coupons/used/", views.UsedCoupons, name="UsedCoupons"),
    path("coupons/used/store/", views.used_coupons_by_member_store, name="used_coupons_by_member_store"),

    # สำหรับเจ้าของร้าน
    path("owner/promotions/", views.promotions_store, name="promotions_store"),
    path("promotion/design/", views.CouponDesign_Store, name="CouponDesign_Store"),
    path("coupon/preview/<int:promotion_id>/", views.CouponPreview, name="CouponPreview"),

    # การใช้งานคูปอง
    path('scan/qrcode/', views.camera_feed, name='camera_feed'),
    path('detect/qrcode/', views.detect, name='detect_qrcode'),
    path('use_coupon/', views.use_coupon, name='use_coupon'),
    path("koupon/qr/<int:store_id>/use/<int:promotion_id>/<int:coupon_id>/", views.use_coupon, name="use_coupon"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# สำหรับการแสดง static file เมื่อ DEBUG = True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
