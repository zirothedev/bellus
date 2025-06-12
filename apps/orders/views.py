import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from apps.cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm

stripe.api_key = settings.STRIPE_SECRET_KEY

def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total_amount = cart.get_total_price()
            order.save()
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Create Stripe payment intent
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total_amount * 100),  # Convert to cents
                    currency='ngn',  # Change to 'ngn' for Nigerian Naira if needed
                    metadata={
                        'order_id': str(order.order_id),
                    }
                )
                order.stripe_payment_intent_id = intent.id
                order.save()
                
                # Store order ID in session for payment processing
                request.session['order_id'] = str(order.order_id)
                
                return redirect('orders:payment', order_id=order.order_id)
            
            except Exception as e:
                messages.error(request, f'Payment setup failed: {str(e)}')
                order.delete()
                return redirect('cart:cart_detail')
    else:
        # Pre-fill form if user is authenticated
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        form = OrderCreateForm(initial=initial_data)
    
    return render(request, 'orders/order_create.html', {
        'cart': cart,
        'form': form
    })

def payment_process(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    
    if request.method == 'POST':
        success_url = request.build_absolute_uri(
            reverse('orders:payment_success', kwargs={'order_id': order.order_id})
        )
        cancel_url = request.build_absolute_uri(
            reverse('orders:payment_cancelled', kwargs={'order_id': order.order_id})
        )
        
        # Update payment intent with success/cancel URLs if using Stripe Checkout
        try:
            stripe.PaymentIntent.modify(
                order.stripe_payment_intent_id,
                metadata={
                    'order_id': str(order.order_id),
                    'success_url': success_url,
                    'cancel_url': cancel_url,
                }
            )
        except Exception as e:
            messages.error(request, f'Payment processing error: {str(e)}')
            
    context = {
        'order': order,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'client_secret': stripe.PaymentIntent.retrieve(
            order.stripe_payment_intent_id
        ).client_secret if order.stripe_payment_intent_id else None,
    }
    
    return render(request, 'orders/payment.html', context)

def payment_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    
    # Verify payment with Stripe
    try:
        intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent_id)
        if intent.status == 'succeeded':
            order.paid = True
            order.status = 'processing'
            order.save()
            
            # Clear the cart
            cart = Cart(request)
            cart.clear()
            
            # Remove order_id from session
            if 'order_id' in request.session:
                del request.session['order_id']
                
            messages.success(request, 'Your payment was successful!')
        else:
            messages.error(request, 'Payment verification failed.')
            
    except Exception as e:
        messages.error(request, f'Payment verification error: {str(e)}')
    
    return render(request, 'orders/payment_success.html', {'order': order})

def payment_cancelled(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    messages.warning(request, 'Payment was cancelled.')
    return render(request, 'orders/payment_cancelled.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required  
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

# apps/orders/urls.py
