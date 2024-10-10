from django.urls import path, include
from Kouponapp import views

urlpatterns = [
    path("", views.promotions_view, name="koupon"),
]
