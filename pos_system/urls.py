# pos_system/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('shops/', views.shop_list, name='shop_list'),
    path('register-shop/', views.register_shop, name='register_shop'),
    path('shop-waiting-approval/', views.shop_waiting_approval, name='shop_waiting_approval'),
]
