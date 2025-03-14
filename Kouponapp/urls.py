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
    path("profile_member/", views.profile_member, name="profile_member"),
    path("profile_store/", views.profile_store, name="profile_store"),
    path("request-store-ownership/", views.request_store_ownership, name="request_store_ownership"),

    # การแสดงโปรโมชั่น
    path("promotions/member/", views.promotions_member, name="promotions_member"),
    path("promotions/all/", views.promotions_all, name="promotions_all"),
    path("promotions/all/details/<int:store_id>/promotion/<int:promotion_id>/", views.promotions_all_details, name="promotions_all_details"),
    path("promotion/details/member/<int:store_id>/<int:promotion_id>/<int:coupon_id>/", views.PromotionDetailsMember, name="PromotionDetailsMember"),

    # คูปองที่ใช้แล้ว
    path("coupon/used/history/", views.coupon_used_history, name="coupon_used_history"),
    path("coupons/used/store/", views.used_coupons_by_member_store, name="used_coupons_by_member_store"),
    path("coupons/expired/", views.expired_coupons, name="expired_coupons"),

    # สำหรับเจ้าของร้าน
    path("owner/promotions/", views.promotions_store, name="promotions_store"),
    path('promotions/expired/', views.expired_promotions_store, name='expired_promotions_store'),
    path('promotion/details/uncollected/<int:promotion_id>/', views.PromotionDetailsUncollected,
    name='promotion_details_uncollected'),
    path('promotion/details/collected/<int:promotion_id>/', views.PromotionDetailsCollected,
    name='promotion_details_collected'),
    path('promotion/details/expired/<int:promotion_id>/', views.PromotionDetailsExpired,
    name='promotion_details_expired'),
    path("promotion/design/", views.CouponDesign_Store, name="CouponDesign_Store"),
    path("coupon/preview/<int:promotion_id>/", views.CouponPreview, name="CouponPreview"),
    path("promotion/details/coupon/<int:promotion_id>/<int:coupon_id>/", views.PromotionDetailsCoupon, name="promotion_details_coupon"),
    path("coupons/member/collect/", views.list_member_collect_coupons, name="list_member_collect_coupons"),

    # การใช้งานคูปอง
    path("scan/qrcode/", views.camera_feed, name="camera_feed"),
    path("detect/qrcode/", views.detect, name="detect_qrcode"),
    path("my/coupons/", views.my_coupons, name="my_coupons"),
    path("koupon/qr/<int:store_id>/collec/<int:promotion_id>/<int:coupon_id>/", views.Collect_coupons, name="collect_coupon"),
    path("coupons/completed/", views.Completed_coupons, name="completed_coupons"),
    path("coupons/pending/", views.Pending_coupons, name="pending_coupons"),
    path("verify/coupons/<int:promotion_id>/", views.verify_coupons, name="verify_coupons"),
    path("verify/pending/coupons/<int:promotion_id>/", views.verify_pending_coupons, name="verify_pending_coupons"),
    path("use/coupon/<int:promotion_id>/", views.use_coupon, name="use_coupon"),
    path("koupon/qr/<int:store_id>/use/<int:promotion_id>/<int:coupon_id>/", views.confirm_coupon_use, name="confirm_coupon_use"),
    path("list/customer/use/coupons/", views.list_customer_use_coupons, name="list_customer_use_coupons"),

    # การจัดการคำขอร้านค้า
    path("request-store/", views.request_store_ownership, name="request_store"),
    path("admin-store-requests/", views.admin_store_requests, name="admin_store_requests"),
    path("store-requests/<int:request_id>/", views.store_request_detail, name="store_request_detail"),
    path("approve-store-request/<int:request_id>/", views.approve_store_request, name="approve_store_request"),

    # การจัดการร้านค้าโดยแอดมิน
    path("admin-stores/", views.admin_store_management, name="admin_store_management"),
    path("admin-stores/<int:store_id>/", views.store_detail, name="store_detail"),
    path("admin-stores/<int:store_id>/delete/", views.delete_store, name="delete_store"),

    # การจัดการสมาชิกโดยแอดมิน
    path("admin-members/", views.admin_member_management, name="admin_member_management"),
    path("admin-members/<int:member_id>/", views.member_detail, name="member_detail"),
    path("admin-members/<int:member_id>/delete/", views.delete_member, name="delete_member"),
    path("admin-members/<int:member_id>/update/", views.update_member_name, name="update_member_name"),

    # การจัดการคูปองโดยแอดมิน
    path("admin-coupons/", views.admin_coupon_management, name="admin_coupon_management"),
    path("admin-coupons/<int:coupon_id>/", views.coupon_detail, name="coupon_detail"),
    path("admin-coupons/delete/<int:coupon_id>/", views.delete_coupon, name="delete_coupon"),

    # การจัดการวอเลต
    path('wallet/', views.my_wallet, name='my_wallet'),
    path('wallet/top-up/', views.top_up, name='wallet_top_up'),
    path('wallet/card/', views.show_card, name='wallet_card'),
    path('wallet/transfer/', views.transfer, name='wallet_transfer'),
    path('wallet/history/', views.transaction_history, name='wallet_history'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# สำหรับการแสดง static file เมื่อ DEBUG = True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)