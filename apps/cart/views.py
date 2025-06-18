from django.shortcuts import render, redirect, get_object_or_404  
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from apps.cart.cart import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem  
from apps.products.models import Product  
from django.db import transaction
import stripe
import requests  # New import for Paystack integration
from django.conf import settings
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.decorators import login_required

# Set your Stripe secret key
stripe.api_key = settings.STRIPE_SECRET_KEY

def cart_detail(request):
    cart = Cart(request)
    total_price = cart.get_total_price() * 100  # Total in kobo

    if request.method == 'POST':
        # Check if user is authenticated before proceeding to payment
        if not request.user.is_authenticated:
            print("User is not authenticated")  # Debugging line
            messages.error(request, 'Please log in before proceeding to payment.')
            return redirect('login')  # Ensure this is the correct URL name

        # Proceed with payment process
        return redirect('cart:payment')  # Redirect to payment view

    context = {
        'cart': cart,
        'total_price': total_price,  # Pass total price to the context
    }
    return render(request, 'cart/cart.html', context)

def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Store checkout data in session
            request.session['checkout_data'] = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone'],
                'address': form.cleaned_data['address'],
                'city': form.cleaned_data['city'],
                'state': form.cleaned_data['state'],
                'zip_code': form.cleaned_data['zip_code'],
                'country': form.cleaned_data['country'],
            }
            return redirect('cart:payment')  # Redirect to payment
        else:
            print(form.errors)  # Debugging line
            return redirect('cart:payment')
            else:
            # Print form errors for debugging
            print(form.errors)  # Add this line
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': '',  # Optional: Pre-fill if needed
            }
        form = CheckoutForm(initial=initial)

    context = {
        'cart': cart,
        'form': form,
        'total': cart.get_total_price() * 100,  # Total in kobo
        'total': cart.get_total_price() * 100,  # Ensure this is in kobo
    }
    return render(request, 'cart/checkout.html', context)

def payment(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    checkout_data = request.session.get('checkout_data')
    if not checkout_data:
        messages.error(request, 'Please complete the checkout form first.')
        return redirect('cart:checkout')

    email = checkout_data.get('email')
    if not email:
        messages.error(request, 'Email is required to proceed with payment.')
        return redirect('cart:checkout')

    return redirect('cart:paystack_checkout')  # Use the namespace for redirect # Redirect to Paystack checkout
    return redirect('paystack_checkout')  # Redirect to Paystack checkout

from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
import requests

@csrf_exempt
def paystack_checkout(request):
    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        email = request.POST.get('email')  # Get email from POST data

        # Check if email is provided; if not, get it from session
        if not email:
            checkout_data = request.session.get('checkout_data')
            email = checkout_data.get('email') if checkout_data else None
        
        if not email:
            messages.error(request, "Email is required.")
            return redirect('cart:checkout')

        # Convert amount to kobo
        try:
            amount = int(float(amount_str) * 100)
        except ValueError:
            messages.error(request, "Invalid amount.")
            return redirect('cart:cart_detail')

        # Initialize Paystack payment
        # Get amount and email from POST data
        amount_str = request.POST.get('amount')
        email = request.POST.get('email')

        # Remove decimal and convert to an integer (in kobo)
        try:
            amount = int(float(amount_str) * 100)  # Convert to kobo
        except ValueError:
            # Handle the error appropriately (e.g., show a message)
            messages.error(request, "Invalid amount.")
            return redirect('cart:cart_detail')

        # Make a request to Paystack to initialize payment
        response = requests.post('https://api.paystack.co/transaction/initialize', json={
            'amount': amount,
            'email': email,
        }, headers={
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Authorization': 'Bearer sk_live_c56dbc2651a1127184ccbdb34d10caa6df280100',  # Replace with your actual secret key
            'Content-Type': 'application/json',
        })

        response_data = response.json()

        if response_data['status']:
            return redirect(response_data['data']['authorization_url'])
        else:
            # Redirect the user to the Paystack payment page
            return redirect(response_data['data']['authorization_url'])
            else:
            # Handle error
            messages.error(request, response_data['message'])
            return redirect('cart:cart_detail')

    return redirect('cart:cart_detail')

def payment_callback(request):
    reference = request.GET.get('reference')
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }

    response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
    verification_data = response.json()

    if verification_data['status']:
        order_id = request.session.get('order_id')
        order = Order.objects.get(id=order_id)
        order.status = 'paid'  # Update status to paid
        order.save()

        # Clear cart
        cart = Cart(request)
        cart.clear()
        del request.session['order_id']

        return render(request, 'cart/payment_success.html', {'order': order})
    else:
        messages.error(request, 'Payment verification failed.')
        return redirect('cart:checkout')

def payment_success(request):
    order_id = request.session.get('order_id')
    if not order_id:
        messages.warning(request, 'No recent order found.')
        return redirect('shop:product_list')

    order = Order.objects.get(id=order_id)
    order.status = 'paid'
    order.save()

    # Clear cart
    cart = Cart(request)
    cart.clear()
    del request.session['order_id']

    return render(request, 'cart/payment_success.html', {'order': order})

def payment_cancelled(request):
    """Handle cancelled payment."""
    messages.warning(request, 'Payment was cancelled.')
    return redirect('cart:checkout')

@require_http_methods(["POST"])
def webhook(request):
    """Handle Stripe webhooks."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']

        try:
            order = Order.objects.get(stripe_payment_intent_id=payment_intent['id'])
            order.status = 'completed'
            order.save()
        except Order.DoesNotExist:
            pass

    return HttpResponse(status=200)

def cart_remove(request, product_id):
    """Remove a product from the cart."""
    cart = Cart(request)
    cart.remove(product_id)  # Pass product_id directly
    messages.success(request, 'Item has been removed from your cart.')
    """Remove an item from the cart."""
    cart = Cart(request)
    cart.remove(product_id)
    messages.success(request, 'Item removed from your cart.')
    return redirect('cart:cart_detail')

def cart_clear(request):
    """Clear the entire cart."""
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Your cart has been cleared.')
    return redirect('cart:cart_detail')

def cart_add(request, product_id):
    """Add a product to the cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product, quantity)
    messages.success(request, f'{product.name} has been added to your cart.')
    return redirect('cart:cart_detail')

def cart_update(request, product_id):
    """Update the quantity of a product in the cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Get the quantity from POST data
    try:
        quantity = int(request.POST.get('quantity', '1'))  # Default to 1 if not provided
    except ValueError:
        quantity = 1  # Fallback to 1 if conversion fails

    if quantity > 0:
        cart.update(product, quantity)
    else:
        cart.remove(product)  # Remove product if quantity is less than or equal to 0

    quantity = int(request.POST.get('quantity', 1))
    cart.update(product, quantity)
    messages.success(request, f'{product.name} quantity has been updated.')
    return redirect('cart:cart_detail')

def apply_promo(request, product_id):
    """Apply a promo code to the cart."""
    cart = Cart(request)
    promo_code = request.POST.get('promo_code')

    if promo_code:
        if promo_code == "DISCOUNT10":
            cart.apply_discount(10)
            messages.success(request, 'Promo code applied successfully!')
        else:
            messages.error(request, 'Invalid promo code.')
    else:
        messages.warning(request, 'Please enter a promo code.')

    return redirect('cart:cart_detail')

class PaymentSuccessView(View):
    def get(self, request):
        return render(request, 'cart/payment_success.html')

def payment_success(request, product_id):
    return render(request, 'cart/payment_success.html')