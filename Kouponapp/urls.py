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
    path('promotion/details/member/<int:store_id>/<int:promotion_id>/<int:coupon_id>/', views.PromotionDetailsMember, name= "PromotionDetailsMember"),

    # คูปองที่ใช้แล้ว
    path('coupon/used/history/', views.coupon_used_history, name='coupon_used_history'),
    path("coupons/used/store/", views.used_coupons_by_member_store, name="used_coupons_by_member_store"),

    # สำหรับเจ้าของร้าน
    path("owner/promotions/", views.promotions_store, name="promotions_store"),
    path("promotion/design/", views.CouponDesign_Store, name="CouponDesign_Store"),
    path("coupon/preview/<int:promotion_id>/", views.CouponPreview, name="CouponPreview"),
    path("owner/promotions/<int:promotion_id>/<int:coupon_id>/", views.PromotionDetailsStore, name= "promotion_details_store"),
    path('coupons/member/collect/', views.list_member_collect_coupons, name='list_member_collect_coupons'),

    # การใช้งานคูปอง
    path('scan/qrcode/', views.camera_feed, name='camera_feed'),
    path('detect/qrcode/', views.detect, name='detect_qrcode'),
    path('my/coupons/', views.my_coupons, name='my_coupons'),
    path('koupon/qr/<int:store_id>/collec/<int:promotion_id>/<int:coupon_id>/', views.Collect_coupons,name='collect_coupon'),
    path('coupons/completed/', views.Completed_coupons, name='completed_coupons'),
    path('coupons/pending/', views.Pending_coupons, name='pending_coupons'),
    path('verify/coupons/<int:promotion_id>/', views.verify_coupons, name='verify_coupons'),
    path('verify/pending/coupons/<int:promotion_id>/', views.verify_pending_coupons, name='verify_pending_coupons'),
    path('use/coupon/<int:promotion_id>/', views.use_coupon, name='use_coupon'),
    path('koupon/qr/<int:store_id>/use/<int:promotion_id>/<int:coupon_id>/', views.confirm_coupon_use, name='confirm_coupon_use'),
    path('list/customer/use/coupons', views.list_customer_use_coupons, name='list_customer_use_coupons'),
    path('request-store/', views.request_store_ownership, name='request_store'),
    path('admin-store-requests/', views.admin_store_requests, name='admin_store_requests'),
    path('store-requests/<int:request_id>/', views.store_request_detail, name='store_request_detail'),
    path('store-requests/<int:request_id>/approve/', views.approve_store_request, name='approve_store_request'),
    path('admin-stores/', views.admin_store_management, name='admin_store_management'),
    path('admin-stores/<int:store_id>/delete/', views.delete_store, name='delete_store'),
    path('admin-stores/<int:store_id>/', views.store_detail, name='store_detail'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# สำหรับการแสดง static file เมื่อ DEBUG = True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)