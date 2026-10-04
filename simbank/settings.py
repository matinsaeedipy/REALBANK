"""
SimBank settings — Django 5.x.

Everything that differs between hosts is controlled with environment variables
(see .env.example / README.md). Defaults are safe for production; running
`python manage.py runserver` switches to development mode automatically.
"""
import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("DATA_DIR") or BASE_DIR)


def env_bool(name, default):
    return os.environ.get(name, "1" if default else "0").strip().lower() in ("1", "true", "yes", "on")


def env_list(name):
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


def _load_secret_key():
    """DJANGO_SECRET_KEY if set, otherwise a key generated once and stored in DATA_DIR."""
    key = os.environ.get("DJANGO_SECRET_KEY")
    if key:
        return key
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        key_file = DATA_DIR / ".secret_key"
        if key_file.exists():
            saved = key_file.read_text().strip()
            if saved:
                return saved
        key = get_random_secret_key()
        key_file.write_text(key)
        try:
            os.chmod(key_file, 0o600)
        except OSError:
            pass
        return key
    except OSError:
        return get_random_secret_key()  # read-only filesystem: sessions reset on restart


SECRET_KEY = _load_secret_key()
DEBUG = env_bool("DJANGO_DEBUG", False)
HTTPS = env_bool("DJANGO_HTTPS", not DEBUG)

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS") or ["*"]
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "bank",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "bank.middleware.LanguageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "bank.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "simbank.urls"
WSGI_APPLICATION = "simbank.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------- Database: SQLite by default, PostgreSQL via DATABASE_URL ----------
_db_url = os.environ.get("DATABASE_URL", "").strip()
if _db_url.startswith(("postgres://", "postgresql://")):
    _u = urlparse(_db_url)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(_u.path.lstrip("/")),
            "USER": unquote(_u.username or ""),
            "PASSWORD": unquote(_u.password or ""),
            "HOST": _u.hostname or "localhost",
            "PORT": str(_u.port or 5432),
            "CONN_MAX_AGE": 60,
            "OPTIONS": {"sslmode": os.environ["DB_SSLMODE"]} if os.environ.get("DB_SSLMODE") else {},
        }
    }
else:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": DATA_DIR / "db.sqlite3",
            "OPTIONS": {"timeout": 20, "transaction_mode": "IMMEDIATE"},
        }
    }

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# ---------- Passwords ----------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------- Language & time ----------
LANGUAGE_CODE = "fa"
LANGUAGES = [("fa", "فارسی"), ("en", "English")]
LANGUAGE_COOKIE_NAME = "simbank_lang"
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "Asia/Tehran")
USE_I18N = True
USE_TZ = True

# ---------- Static files (served by WhiteNoise, no nginx needed) ----------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
WHITENOISE_USE_FINDERS = True          # works even if collectstatic was not run
WHITENOISE_AUTOREFRESH = DEBUG

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# ---------- Security ----------
SESSION_COOKIE_AGE = 15 * 60          # 15 minutes of inactivity = automatic sign-out
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = HTTPS
CSRF_COOKIE_SECURE = HTTPS
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SECURE_SSL_REDIRECT = env_bool("DJANGO_SSL_REDIRECT", False)
SECURE_HSTS_SECONDS = 31536000 if (HTTPS and not DEBUG) else 0
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 50

# Behind a reverse proxy / PaaS load balancer that terminates HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO")},
}

# ---------- Bank rules ----------
OPENING_BALANCE = 1_000_000          # simulated starting balance
MAX_SINGLE_TRANSFER = 20_000_000
DAILY_TRANSFER_LIMIT = 50_000_000
