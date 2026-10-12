import os
from pathlib import Path
from dotenv import load_dotenv


# ============================================================
# BASE DIRECTORY & ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")


# Convert comma-separated environment variable into a Python list
def env_list(name, default=""):
    return [
        v.strip()
        for v in os.environ.get(name, default).split(",")
        if v.strip()
    ]


# ============================================================
# SECURITY SETTINGS
# ============================================================

# Django secret key
SECRET_KEY = os.environ.get(
    "SECRET_KEY"
) or "django-insecure-development-key-only"

# Enable/Disable Django Debug Mode
DEBUG = os.environ.get("DEBUG", "True").lower() in (
    "1",
    "true",
    "yes",
)

# Allowed domains/hosts
ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost",
)

# Trusted CSRF origins
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")


# ============================================================
# INSTALLED APPS
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",

    # Third-party applications
    "rest_framework",
    "rest_framework.authtoken",

    # Project applications
    "accounts",
    "jobs",
    "applications",
    "dashboard",
    "notifications",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL & WSGI CONFIGURATION
# ============================================================

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"


# ============================================================
# TEMPLATE CONFIGURATION
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        # Project-level templates directory
        "DIRS": [BASE_DIR / "templates"],

        # Search templates inside installed apps
        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                # Notification context processor
                "notifications.context_processors.notification_context",
            ],
        },
    },
]


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ============================================================
# AUTHENTICATION CONFIGURATION
# ============================================================

# Custom User Model
AUTH_USER_MODEL = "accounts.User"

# Login and redirect URLs
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"


# ============================================================
# STATIC & MEDIA FILES
# ============================================================

# Static files
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Uploaded media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Private uploaded files
PRIVATE_MEDIA_ROOT = BASE_DIR / "private_media"


# ============================================================
# GENERAL DJANGO SETTINGS
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Enable timezone-aware datetime
USE_TZ = True


# ============================================================
# SECURITY HEADERS
# ============================================================

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# ============================================================
# PRODUCTION SECURITY SETTINGS
# ============================================================

if not DEBUG:
    # Redirect HTTP requests to HTTPS in production
    SECURE_SSL_REDIRECT = os.environ.get(
        "SECURE_SSL_REDIRECT",
        "True",
    ).lower() in (
        "1",
        "true",
        "yes",
    )

    # Secure cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HTTP Strict Transport Security (HSTS)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

else:
    # Do not force HTTPS during local development
    SECURE_SSL_REDIRECT = False


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    # Authentication methods
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],

    # Default permission
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],

    # Pagination
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 12,

    # API request throttling
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],

    # Throttle rates
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
        "user": "300/min",
    },
}


# ============================================================
# EMAIL CONFIGURATION
# ============================================================

# Email backend
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

# SMTP server configuration
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))

# Enable TLS for email
EMAIL_USE_TLS = os.environ.get(
    "EMAIL_USE_TLS",
    "True",
).lower() in (
    "1",
    "true",
    "yes",
)

# Email account credentials
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

# Default sender email
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER or "bbharatbasnet@gmail.com",
)


# ============================================================
# FILE UPLOAD LIMIT
# ============================================================

# Maximum uploaded file size: 5 MB
MAX_UPLOAD_SIZE = 5 * 1024 * 1024