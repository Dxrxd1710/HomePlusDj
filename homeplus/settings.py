from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
"""
HOME+ - Configuración de Django
"""

# ─────────────────────────────────────────
# APLICACIONES INSTALADAS
# ─────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # App de usuarios
    'usuarios',
    'servicios.apps.ServiciosConfig',
]


# ─────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ─────────────────────────────────────────
# URLS PRINCIPALES
# ─────────────────────────────────────────
ROOT_URLCONF = 'homeplus.urls'


# ─────────────────────────────────────────
# WSGI
# ─────────────────────────────────────────
WSGI_APPLICATION = 'homeplus.wsgi.application'


# ─────────────────────────────────────────
# BASE DE DATOS - MySQL Workbench
# ─────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'homejd',
        'USER': 'root',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '3307',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}


# ─────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # 👇 AQUÍ ESTÁ LA CLAVE
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


# ─────────────────────────────────────────
# ARCHIVOS ESTÁTICOS
# ─────────────────────────────────────────
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]
STATIC_ROOT = 'staticfiles'


# ─────────────────────────────────────────
# ARCHIVOS MEDIA (imagenes de usuarios etc)
# ─────────────────────────────────────────
MEDIA_URL = '/media/'

MEDIA_ROOT = 'media'


# ─────────────────────────────────────────
# CORREO ELECTRÓNICO
# ─────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'adminhomeplus@gmail.com'
EMAIL_HOST_PASSWORD = 'hvrumebwnjynkmdy'


# ─────────────────────────────────────────
# SESIONES
# ─────────────────────────────────────────
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SESSION_COOKIE_AGE = 86400


# ─────────────────────────────────────────
# SEGURIDAD
# ─────────────────────────────────────────
SECRET_KEY = 'homeplus-cambia-esta-clave-secreta-en-produccion-abc123xyz'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# ─────────────────────────────────────────
# INTERNACIONALIZACIÓN
# ─────────────────────────────────────────
LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# ─────────────────────────────────────────
# DEFAULT AUTO FIELD
# ─────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
