import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
ON_RENDER = os.getenv("RENDER") == "true"
DEBUG = not ON_RENDER and os.getenv("DJANGO_DEBUG") == "1"
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("Configura SECRET_KEY.")
    SECRET_KEY = "django-insecure-local-chicla-desarrollo-solamente"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
if render_host := os.getenv("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(render_host)
ALLOWED_HOSTS.extend(host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if host.strip())

INSTALLED_APPS = [
    "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions",
    "django.contrib.messages", "django.contrib.staticfiles", "expedientes",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "expedientes.middleware.ExpireInactiveSession",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "sgd.urls"
WSGI_APPLICATION = "sgd.wsgi.application"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "expedientes.context.release",
    ]},
}]

DATABASES = {"default": dj_database_url.config(
    default="postgresql://sgd:sgd_local@127.0.0.1:5432/sgd", conn_max_age=0,
)}
if DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
    raise ImproperlyConfigured("SGD Chicla requiere PostgreSQL.")
DATABASES["default"].setdefault("OPTIONS", {}).setdefault("connect_timeout", 5)
AUTH_USER_MODEL = "expedientes.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 15}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

LOGIN_URL = "login"
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_NAME = "chicla_session"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_IDLE_SECONDS = int(os.getenv("SESSION_IDLE_SECONDS", "300"))
if not 30 <= SESSION_IDLE_SECONDS <= 3600:
    raise ImproperlyConfigured("SESSION_IDLE_SECONDS debe estar entre 30 y 3600.")
SESSION_COOKIE_AGE = SESSION_IDLE_SECONDS + 60
SECURE_BROWSER = ON_RENDER or os.getenv("DJANGO_HTTPS") == "1"
SESSION_COOKIE_SECURE = SECURE_BROWSER
CSRF_COOKIE_SECURE = SECURE_BROWSER
SECURE_SSL_REDIRECT = SECURE_BROWSER
SECURE_REDIRECT_EXEMPT = [r"^salud/$"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if ON_RENDER else None
SECURE_HSTS_SECONDS = 31536000 if SECURE_BROWSER else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_BROWSER
# Preloading requires a separate decision and is unnecessary for the Render subdomain.
SILENCED_SYSTEM_CHECKS = ["security.W021"]
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
CSRF_FAILURE_VIEW = "expedientes.views.csrf_failure"

DATA_UPLOAD_MAX_MEMORY_SIZE = 128 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 256 * 1024
DATA_UPLOAD_MAX_NUMBER_FILES = 1
MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024
ATTACHMENT_QUOTA_BYTES = 100 * 1024 * 1024
RELEASE = os.getenv("RENDER_GIT_COMMIT", "local")
