from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),
    path('paystack/checkout/', views.paystack_checkout, name='paystack_checkout'),  # Paystack checkout
    path('payment/callback/', views.payment_callback, name='payment_callback'),  # Paystack callback
    path('success/', views.payment_success, name='payment_success'),
    path('cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),  # Remove item from cart
    path('clear/', views.cart_clear, name='cart_clear'),  # Clear the cart
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),  # Add item to cart
    path('update/<int:product_id>/', views.cart_update, name='cart_update'),  # Update item in cart
    path('apply-promo/', views.apply_promo, name='apply_promo'),  # Apply promo code
]