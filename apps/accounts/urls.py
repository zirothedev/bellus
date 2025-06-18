from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

app_name = 'accounts'

from django.urls import reverse_lazy

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        authentication_form=CustomAuthenticationForm,
        extra_context={'title': 'Login'}
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('core:home')), name='logout'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    path('register/', views.register_view, name='register'),
    
    path('profile/', views.profile_view, name='profile'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
    ), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('orders/', views.order_history, name='order_history'),
]