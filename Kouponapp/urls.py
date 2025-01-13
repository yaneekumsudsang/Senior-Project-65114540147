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
    path('promotion/<int:store_id>/<int:promotion_id>/<int:coupon_id>/',views.PromotionDetails,name= 'promotion_details'),

    # คูปองที่ใช้แล้ว
    path("coupons/used/", views.UsedCoupons, name="UsedCoupons"),
    path("coupons/used/store/", views.used_coupons_by_member_store, name="used_coupons_by_member_store"),

    # สำหรับเจ้าของร้าน
    path("owner/promotions/", views.promotions_store, name="promotions_store"),
    path("promotion/design/", views.CouponDesign_Store, name="CouponDesign_Store"),
    path("coupon/preview/<int:promotion_id>/", views.CouponPreview, name="CouponPreview"),
    path("owner/promotions/<int:promotion_id>/<int:coupon_id>/", views.PromotionDetailsStore, name="promotion_details_store"),

    # การใช้งานคูปอง
    path('scan/qrcode/', views.camera_feed, name='camera_feed'),
    path('detect/qrcode/', views.detect, name='detect_qrcode'),
    #path('Collect/coupons/', views.Collect_coupons, name='Collect_coupons'),
    path('my/coupons/', views.my_coupons, name='my_coupons'),
    path('koupon/qr/<int:store_id>/<int:promotion_id>/<int:coupon_id>/', views.Collect_coupons, name='collect_coupon'),
    path('coupon/scan/<int:coupon_id>/', views.update_collect_status, name='update_collect_status'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# สำหรับการแสดง static file เมื่อ DEBUG = True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)