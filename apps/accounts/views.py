from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, UserProfileForm
from django.contrib.auth import logout


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Account created for {username}! You can now log in.')
        return response

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def dashboard_view(request):
    # Get user's recent orders
    from apps.orders.models import Order
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to a desired page after logout

# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm
from django import forms
from apps.orders.models import Order  # Correct import if in the same directory structure # Assuming your orders app has an Order model

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    phone = forms.CharField(
        max_length=15, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'})
    )
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Shipping address'}),
        required=False
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

@login_required
def dashboard(request):
    """User dashboard view"""
    # Get user's recent orders (assuming you have an Order model)
    try:
        recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    except:
        recent_orders = []  # Handle case where Order model doesn't exist yet
    
    # Get user profile data
    user_profile = {
        'phone': getattr(request.user, 'phone', ''),
        'shipping_address': getattr(request.user, 'shipping_address', ''),
    }
    
    context = {
        'user': request.user,
        'recent_orders': recent_orders,
        'user_profile': user_profile,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def edit_profile(request):
    """Edit user profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            # Save additional profile fields if you extend the User model
            # or use a separate UserProfile model
            phone = form.cleaned_data.get('phone')
            shipping_address = form.cleaned_data.get('shipping_address')
            
            # You might need to create a UserProfile model to store these fields
            # For now, we'll assume you extend the User model or handle this differently
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:dashboard')
    else:
        initial_data = {
            'phone': getattr(request.user, 'phone', ''),
            'shipping_address': getattr(request.user, 'shipping_address', ''),
        }
        form = UserProfileForm(instance=request.user, initial=initial_data)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def order_history(request):
    """View all user orders"""
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    except:
        orders = []
    
    return render(request, 'accounts/order_history.html', {'orders': orders})

# accounts/views.py (Updated version with UserProfile support)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm
from django import forms
from apps.orders.models import Order   # Assuming your orders app has an Order model
from .models import UserProfile  # If you're using the UserProfile model

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    phone = forms.CharField(
        max_length=15, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Phone number'
        })
    )
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3, 
            'placeholder': 'Enter your full shipping address'
        }),
        required=False
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Extract user profile data if available
        user = kwargs.get('instance')
        if user and hasattr(user, 'profile'):
            kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['phone'] = user.profile.phone
            kwargs['initial']['shipping_address'] = user.profile.shipping_address
        
        super().__init__(*args, **kwargs)

@login_required
def dashboard(request):
    """User dashboard view"""
    # Get user's recent orders
    try:
        recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    except:
        recent_orders = []  # Handle case where Order model doesn't exist yet
    
    # Get user profile data
    user_profile = {}
    if hasattr(request.user, 'profile'):
        user_profile = {
            'phone': request.user.profile.phone or '',
            'shipping_address': request.user.profile.shipping_address or '',
        }
    else:
        # Fallback if not using UserProfile model
        user_profile = {
            'phone': getattr(request.user, 'phone', ''),
            'shipping_address': getattr(request.user, 'shipping_address', ''),
        }
    
    context = {
        'user': request.user,
        'recent_orders': recent_orders,
        'user_profile': user_profile,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def edit_profile(request):
    """Edit user profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            
            # Save additional profile fields
            phone = form.cleaned_data.get('phone')
            shipping_address = form.cleaned_data.get('shipping_address')
            
            # If using UserProfile model
            if hasattr(user, 'profile'):
                user.profile.phone = phone
                user.profile.shipping_address = shipping_address
                user.profile.save()
            else:
                # If extending User model directly (you'd need to add these fields to User)
                # user.phone = phone
                # user.shipping_address = shipping_address
                # user.save()
                pass
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def order_history(request):
    """View all user orders"""
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    except:
        orders = []
    
    return render(request, 'accounts/order_history.html', {'orders': orders})

# Additional views you might need

@login_required
def change_password(request):
    """Change password view (optional)"""
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('accounts:dashboard')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})
    return redirect('home')  # Redirect to a desired page after logout
