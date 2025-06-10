from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('payment/<uuid:order_id>/', views.payment_process, name='payment'),
    path('payment/success/<uuid:order_id>/', views.payment_success, name='payment_success'),
    path('payment/cancelled/<uuid:order_id>/', views.payment_cancelled, name='payment_cancelled'),
    path('history/', views.order_history, name='order_history'),
    path('<uuid:order_id>/', views.order_detail, name='order_detail'),
]