"""
Django settings for SmartSightCapstoneProject project.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------
# SECURITY WARNINGS
# -------------------
# 1. Use environment variables for production SECRET_KEY
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-kr&v(s#%h9o+s+gdp6yd*)n@a4&%83$9p+t%q!rxf0x@3(*c%v')

# 2. DEBUG setting is set based on environment variable (safer for Render)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# -------------------
# Allowed Hosts
# -------------------
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "192.168.1.10",
    "83bc02744841.ngrok-free.app",
    # ✅ PRODUCTION HOST: Required to fix DisallowedHost
    "smartsight-admin.onrender.com",
]

# Dynamically add ngrok host if set
NGROK_URL = os.environ.get("NGROK_URL")
if NGROK_URL and NGROK_URL not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(NGROK_URL)

# Redirect unauthenticated users to login
LOGIN_URL = '/login/'

# -------------------
# Installed Apps
# -------------------
INSTALLED_APPS = [
    # Third-party app for production static files
    # Note: Make sure you installed 'whitenoise' (pip install whitenoise)
    'whitenoise.runserver_nostatic', 

    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your local apps
    'admin_panel.apps.AdminPanelConfig',

    # Channels (WebSocket support)
    'channels',

    # REST API and CORS
    'rest_framework',
    'corsheaders',
    'rest_framework.authtoken',
]

# -------------------
# Middleware
# -------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # ✅ WhiteNoise Middleware: Must be placed after SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware', 

    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -------------------
# URL Configuration
# -------------------
ROOT_URLCONF = 'admin_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# -------------------
# WSGI / ASGI Configuration
# -------------------
WSGI_APPLICATION = 'admin_site.wsgi.application'
ASGI_APPLICATION = 'admin_site.asgi.application' 

# -------------------
# Database
# -------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.rgoancdcxnbstttjutbq',
        'PASSWORD': 'Pining_06090',
        'HOST': 'aws-1-ap-south-1.pooler.supabase.com',
        'PORT': '5432',
    }
}

# -------------------
# Password Validation
# -------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------
# Internationalization
# -------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

# -------------------
# Static Files and Media
# -------------------
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ PRODUCTION STATIC FILES SETTINGS (Needed for Render):
# Location where 'collectstatic' will place all files
STATIC_ROOT = BASE_DIR / 'staticfiles' 

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# -------------------
# CORS and CSRF Settings
# -------------------
CORS_ALLOW_ALL_ORIGINS = True 
CSRF_COOKIE_NAME = "X-CSRFToken"

# ✅ CSRF FIX: Required to fix 403 Forbidden (CSRF verification failed)
CSRF_TRUSTED_ORIGINS = [
    'https://capstone-defended-final.onrender.com',
]

# If NGROK is set, ensure its HTTPS version is also trusted
if NGROK_URL:
    CSRF_TRUSTED_ORIGINS.append(f"https://{NGROK_URL}")

# -------------------
# Channels / Redis Setup (for real-time notifications)
# -------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer", 
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# -------------------
# REST Framework Configuration
# -------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# -------------------
# Email Configuration
# -------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# NOTE: Highly recommend using Environment Variables for credentials
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'rosmillago@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'qblo qmcm owjj thnl')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

