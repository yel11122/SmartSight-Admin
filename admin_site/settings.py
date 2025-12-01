"""
Django settings for SmartSightCapstoneProject project.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-kr&v(s#%h9o+s+gdp6yd*)n@a4&%83$9p+t%q!rxf0x@3(*c%v'
DEBUG = True

# -------------------
# Allowed Hosts
# -------------------
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "192.168.1.10",
    "83bc02744841.ngrok-free.app",
]

# ✅ Dynamically add ngrok host if set
NGROK_URL = os.environ.get("NGROK_URL")
if NGROK_URL and NGROK_URL not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(NGROK_URL)

# Redirect unauthenticated users to login
LOGIN_URL = '/login/'

# -------------------
# Installed Apps
# -------------------
INSTALLED_APPS = [
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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # ✅ Must be before CommonMiddleware
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
ASGI_APPLICATION = 'admin_site.asgi.application'  # ✅ For Channels/WebSocket support

# -------------------
# Database
# -------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'capstone',
        'HOST': 'localhost',
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
# Static Files
# -------------------
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------
# CORS Settings
# -------------------
CORS_ALLOW_ALL_ORIGINS = True  # ✅ Open access during dev (secure later)
CSRF_COOKIE_NAME = "X-CSRFToken"

# -------------------
# Channels / Redis Setup (for real-time notifications)
# -------------------
# Requires: pip install channels channels_redis redis
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer", #Later, for production, switch to Redis:         "BACKEND": "channels_redis.core.RedisChannelLayer",
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

# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'rosmillago@gmail.com'
EMAIL_HOST_PASSWORD = 'qblo qmcm owjj thnl'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


#STOP