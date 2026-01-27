import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠️ Use environment variable for secret key in production
SECRET_KEY = os.environ.get("SECRET_KEY", "replace-this-with-your-secret-key")

# ⚠️ Debug should be False in production
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "192.168.1.236",  # local network dev
    "martin1988asia.pythonanywhere.com",  # production domain
    "atomic-technology.com",              # production DB host (after upgrade)
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework_simplejwt",
    "drf_yasg",
    "corsheaders",

    "accounts",
    "users",
    "courses",
    "assignments",
    "grades",
    "analytics",
    "enrollments",
    "django_extensions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # must be high in the list
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lms_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "lms_project" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "lms_backend.wsgi.application"

# ✅ PostgreSQL database connection
# Local DB for development until remote server is upgraded
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "lms_local",        # local database name
        "USER": "postgres",         # default local postgres user
        "PASSWORD": os.environ.get("DB_PASSWORD", "Felicia@2025"),  # ✅ supply password
        "HOST": "127.0.0.1",        # local machine
        "PORT": "5432",             # default PostgreSQL port
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Windhoek"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.CustomUser"

# ✅ Enable email-based authentication backend
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailBackend",             # custom backend for email login
    "django.contrib.auth.backends.ModelBackend",  # keep default for admin login
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ✅ CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # dev React
    "https://martin1988asia.pythonanywhere.com",  # prod
]
CORS_ALLOW_CREDENTIALS = True

# ✅ Email settings
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)  # console for dev, SMTP in prod
DEFAULT_FROM_EMAIL = "noreply@yourdomain.com"
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
