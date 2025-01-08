from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.promotions_view, name="home"),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('promotions_member/', views.promotions_member, name='promotions_member'),
    path('koupon_logout/', views.koupon_logout, name='koupon_logout'),
    path('profile/', views.profile_view, name='profile'),
    path('promotions/', views.promotion_list, name='promotion_list'),
    path('UsedCoupons/', views.UsedCoupons, name='UsedCoupons'),
    path('promotion/<int:id>/', views.PromotionDetails, name='promotion_details'),
    path('promotions_all/', views.promotions_all, name='promotions_all'),
    path('owner/promotions/', views.promotions_store, name='promotions_store'),
    path('used_coupons_by_member_store/', views.used_coupons_by_member_store, name='used_coupons_by_member_store'),
    path('promotion/design/', views.CouponDesign_Store, name='CouponDesign_Store'),
    path('coupon_preview/<int:promotion_id>/', views.CouponPreview, name='CouponPreview'),
    path('koupon/qr/<str:username>/use/<int:promotion_id>/<int:count>/', views.CouponPreview, name='use_coupon'),
    path('koupon/qr/<int:store_id>/use/<int:promotion_id>/<int:coupon_id>', views.use_coupon, name='use_coupon'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
