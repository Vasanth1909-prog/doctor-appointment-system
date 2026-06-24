"""
Django settings for docappsystem project.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = 'django-insecure-=u!!em!u$#9d=ew1uzeq&=90w(%62nx5b)9j66kbhh2*ee__il'
DEBUG = True
ALLOWED_HOSTS = ['*']

# APPLICATIONS
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dasapp',
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
    

ROOT_URLCONF = 'docappsystem.urls'

# TEMPLATES
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
            ],
        },
    },
]

WSGI_APPLICATION = 'docappsystem.wsgi.application'

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# PASSWORD VALIDATION
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# STATIC FILES
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CUSTOM USER
AUTH_USER_MODEL = 'dasapp.CustomUser'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================================
# ✅ EMAIL CONFIGURATION (GMAIL WORKING)
# =========================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'vasanthvasi532@gmail.com'   # 🔴 CHANGE THIS
EMAIL_HOST_PASSWORD = 'pbuztzqyanvuaxlc'  # 🔴 CHANGE THIS

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# =========================================
# 💰 RAZORPAY
# =========================================
RAZORPAY_KEY_ID = ""
RAZORPAY_KEY_SECRET = ""

# =========================================
# 📱 TWILIO (SMS)
# =========================================
TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_PHONE_NUMBER = ''

# =========================================
# 🎥 VIDEO LINK
# =========================================
VIDEO_CONFERENCE_URL = 'https://meet.jit.si/'

# =========================================
# 🎨 JAZZMIN UI
# =========================================
JAZZMIN_SETTINGS = {
    "site_title": "Hospital Admin",
    "site_header": "Hospital Appointment Admin",
    "site_brand": "HospitalCare",
    "welcome_sign": "Welcome to Hospital Appointment Management System",
    "copyright": "HospitalCare",
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "dasapp.CustomUser": "fas fa-user-shield",
        "dasapp.DoctorReg": "fas fa-user-md",
        "dasapp.Specialization": "fas fa-stethoscope",
        "dasapp.Appointment": "fas fa-calendar-check",
        "dasapp.Page": "fas fa-globe",
        "dasapp.Payment": "fas fa-credit-card",
        "dasapp.SMSLog": "fas fa-sms",
    },
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "navbar": "navbar-primary navbar-dark",
    "accent": "accent-primary",
}