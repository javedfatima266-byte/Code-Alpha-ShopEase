"""
Django settings for ShopEase project.

Generated for ShopEase internship e-commerce project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables if available
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except Exception:
    pass

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    os.environ.get(
        'SECRET_KEY',
        'django-insecure-shopease-internship-fullstack-key-2026-secure-token'
    )
)
   

DEBUG = os.environ.get('DEBUG', 'True').strip().lower() in ('true', '1', 'yes')

# Reverse Proxy & Host Header Resolution
# Ensures Django correctly recognizes the Cloud Run host when forwarded by Nginx
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

allowed_hosts_env = os.environ.get('ALLOWED_HOSTS')
if allowed_hosts_env and allowed_hosts_env.strip() != '*':
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
else:
    # Allow all hosts in development and Cloud Run preview
    ALLOWED_HOSTS = ['*']

# Automatically include Cloud Run service host from environment if present
ng_allowed = os.environ.get('NG_ALLOWED_HOSTS', '').strip()
if ng_allowed and ng_allowed not in ALLOWED_HOSTS and '*' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(ng_allowed)
    # CSRF Trusted Origins Configuration
CSRF_TRUSTED_ORIGINS = [
    'https://*.run.app',
    'https://*.asia-east1.run.app',
    'https://*.google.com',
    'https://*.googleusercontent.com',
    'https://*.aistudio.google.com',

    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000',
]

csrf_trusted_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '').strip()

if csrf_trusted_env:
    for origin in csrf_trusted_env.split(','):
        cleaned = origin.strip()

        if cleaned and cleaned.startswith(('http://', 'https://')):
            if cleaned not in CSRF_TRUSTED_ORIGINS:
                CSRF_TRUSTED_ORIGINS.append(cleaned)


# Frame options & cookie configuration
# AI Studio renders the application inside a cross-site iframe.
# In Cloud Run / preview (HTTPS), cookies require SameSite=None and Secure=True
# so that browser third-party cookie policies do not drop session or CSRF cookies.
is_cloud_run = bool(os.environ.get('K_SERVICE') or ng_allowed)

if is_cloud_run:
    CSRF_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'ALLOWALL'
elif not DEBUG:
    # Standard standalone production deployment
    X_FRAME_OPTIONS = os.environ.get('X_FRAME_OPTIONS', 'DENY')
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() in ('true', '1')
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() in ('true', '1')
    CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'True').lower() in ('true', '1')
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
else:
    # Pure local HTTP development
    X_FRAME_OPTIONS = 'ALLOWALL'
    CSRF_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ShopEase store application
    'store.apps.StoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Clickjacking protection is enabled in production
if not DEBUG:
    MIDDLEWARE.append('django.middleware.clickjacking.XFrameOptionsMiddleware')

ROOT_URLCONF = 'shopease.urls'

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
                'store.context_processors.store_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'shopease.wsgi.application'

# Database
# Default is SQLite for easy local development.
# Structure allows switching to PostgreSQL via DATABASE_URL or environment variables.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Optional PostgreSQL configuration if DATABASE_URL is provided
if os.environ.get('DATABASE_URL'):
    try:
        import dj_database_url
        DATABASES['default'] = dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    except ImportError:
        pass

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
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
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (Product uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Django Messages Framework styling tags
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'info',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
