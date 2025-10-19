# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('confirm/', views.order_confirm_view, name='order_confirm_view'),
    path('payment/', views.payment_page, name='payment_page'),
    path('verify/', views.verify_payment, name='verify'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
]