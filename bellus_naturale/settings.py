# bellus_naturale/settings.py
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']
ALLOWED_HOSTS = ['bellus.onrender.com']

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.products',
    'apps.cart',
    'apps.orders',
    'apps.pages',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bellus_naturale.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.cart.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = 'bellus_naturale.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = config('pk_test_51RT1EFGg76wVayeaqg5jQDQV8O1HDMnNZUUObL8U8RKQb8mgKYMPn8DCoMQRtKVDgKqEOnWSuJrRaNNFIYBAJ6qO006RaE9mB6', default='')
STRIPE_SECRET_KEY = config('sk_test_51RT1EFGg76wVayeaNq2dZzQeKGkquazaTbtfjKxvcgMr3v2GDqzgWAXrvJKX9DIQgSOmgm22qEiptNC9Bby0ZOHF00V577oOWE', default='')
PAYSTACK_PUBLIC_KEY = 'pk_test_c3aecf546bd0e42136ddb357bd0615f0d3299916'
PAYSTACK_SECRET_KEY = 'sk_test_5cf7f727ecb6f0016e4b85b65bfbe4cdb71960d8'
PAYSTACK_PUBLIC_KEY = 'pk_live_472d55665abc1cd0852af6cfdef2da5f0fb75dfa'
PAYSTACK_SECRET_KEY = 'sk_live_c56dbc2651a1127184ccbdb34d10caa6df280100'
# Email Configuration (for contact forms)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Change to SMTP in production
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Session Configuration
CART_SESSION_ID = 'cart'
SESSION_COOKIE_AGE = 86400  # 1 day

# Custom User Model (if you want to extend it later)
# AUTH_USER_MODEL = 'accounts.CustomUser'
# AUTH_USER_MODEL = 'accounts.CustomUser'
CSRF_TRUSTED_ORIGINS = [
    'https://bellus.onrender.com',
]
