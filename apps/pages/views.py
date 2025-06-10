# apps/pages/views.py
from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from apps.products.models import Product, Category
from .forms import ContactForm

def home(request):
    # Get featured products
    featured_products = Product.objects.filter(featured=True, available=True)[:8]
    
    # Get categories for navigation
    categories = Category.objects.all()[:6]
    
    # Get new arrivals
    new_arrivals = Product.objects.filter(available=True).order_by('-created_at')[:4]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'new_arrivals': new_arrivals,
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'pages/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Send email (configure email backend in settings)
            try:
                send_mail(
                    subject=f'Contact Form: {subject}',
                    message=f'From: {name} <{email}>\n\n{message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['info@bellusnaturale.com'],  # Replace with your email
                    fail_silently=False,
                )
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
                return render(request, 'pages/contact.html', {'form': ContactForm()})
            except Exception as e:
                messages.error(request, 'There was an error sending your message. Please try again.')
    else:
        form = ContactForm()
    
    return render(request, 'pages/contact.html', {'form': form})
