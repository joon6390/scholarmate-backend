"""
Django settings for ScholarMate_backend project.
"""
import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from corsheaders.defaults import default_headers  # ✅ CORS 기본 헤더 확장용
from urllib.parse import unquote, urlparse

# .env 로드
load_dotenv()

# ===== 경로 & 기본 =====
BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default):
    value = os.environ.get(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "your-default-secret-key-for-dev")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,34.228.112.95"
)

RAILWAY_PUBLIC_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
RAILWAY_PRIVATE_DOMAIN = os.environ.get("RAILWAY_PRIVATE_DOMAIN")
for railway_domain in (RAILWAY_PUBLIC_DOMAIN, RAILWAY_PRIVATE_DOMAIN):
    if railway_domain and railway_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(railway_domain)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", not DEBUG)
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", not DEBUG)
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", False
)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", False)

# ===== 국제화(i18n) / 시간대 =====
LANGUAGE_CODE = "ko-kr"
USE_I18N = True
TIME_ZONE = "Asia/Seoul"   # 표시/입력 기준
USE_TZ = True              # DB 저장은 UTC (권장)

# ===== 이메일 인증 코드(커스텀 기능용) =====
EMAIL_VERIFICATION_CODE_TTL = 120
EMAIL_VERIFICATION_COOLDOWN = 60
ENABLE_EMAIL_VERIFICATION = True

# ===== 캐시 =====
REDIS_CACHE_URL = os.environ.get("REDIS_CACHE_URL") or os.environ.get("REDIS_URL")
if REDIS_CACHE_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_CACHE_URL,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
            "KEY_PREFIX": "scholarmate",
            "TIMEOUT": 300,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "scholarmate-local",
            "TIMEOUT": 300,
        }
    }

# ===== 이메일(SMTP) =====
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.naver.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "joon6390@naver.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_FILE_PATH = os.getenv("EMAIL_FILE_PATH", str(BASE_DIR / "local_emails"))
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST_PASSWORD
    else "django.core.mail.backends.filebased.EmailBackend",
)
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "False") == "True"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "True") == "True"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

_CONTACT_ADMIN_EMAILS = [
    e.strip() for e in os.getenv("CONTACT_ADMIN_EMAILS", "").split(",") if e.strip()
]
CONTACT_ADMIN_EMAILS = (
    _CONTACT_ADMIN_EMAILS
    or ([DEFAULT_FROM_EMAIL] if EMAIL_BACKEND.endswith("filebased.EmailBackend") else [])
)

# ===== 앱 =====
INSTALLED_APPS = [
    # django 기본
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 추가
    "django.contrib.sites",        # 비번재설정 링크 도메인 구성용
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework.authtoken",
    "djoser",
    "corsheaders",
    "django_filters",

    # 프로젝트 앱
    "scholarships",
    "userinfor",
    "contact",
    "accounts",
    "notices",
    "community",
]

SITE_ID = 1

# ===== DRF =====
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

# ===== JWT =====
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer", "JWT"),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "ALGORITHM": "HS256",
}

# ===== Djoser (비번재설정 핵심) =====
DJOSER = {
    "USER_ID_FIELD": "username",
    "SERIALIZERS": {
        "user_create": "accounts.serializers.UserCreateSerializer",
        "user": "accounts.serializers.CustomUserSerializer",
        "current_user": "accounts.serializers.CustomUserSerializer",
    },
    "PASSWORD_RESET_CONFIRM_URL": "reset-password?uid={uid}&token={token}",
    "PERMISSIONS": {
        "password_reset": ["rest_framework.permissions.AllowAny"],
        "password_reset_confirm": ["rest_framework.permissions.AllowAny"],
        "user_create": ["rest_framework.permissions.AllowAny"],
        "user": ["rest_framework.permissions.IsAuthenticated"],
        "set_password": ["rest_framework.permissions.IsAuthenticated"],
    },
    # ✅ 프론트엔드 현재 주소만 사용
    "DOMAIN": os.getenv("FRONTEND_DOMAIN", "https://scholar-mate-chi.vercel.app"),
    "SITE_NAME": "ScholarMate",
}

# ===== 미들웨어 =====
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",            # ✅ 최상단 배치 권장
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ===== CORS/CSRF =====
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://34.228.112.95,https://scholar-mate-chi.vercel.app",
)
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "content-type",
]

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:5173,http://34.228.112.95,https://scholar-mate-chi.vercel.app",
)

if RAILWAY_PUBLIC_DOMAIN:
    railway_origin = f"https://{RAILWAY_PUBLIC_DOMAIN}"
    if railway_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(railway_origin)

ROOT_URLCONF = "ScholarMate_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ScholarMate_backend.wsgi.application"

# ===== DB =====
USE_SQLITE = env_bool("DJANGO_USE_SQLITE", False)
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("MYSQL_URL")
MYSQL_DATABASE = {
    "NAME": os.environ.get("DATABASE_NAME") or os.environ.get("MYSQLDATABASE"),
    "USER": os.environ.get("DATABASE_USER") or os.environ.get("MYSQLUSER"),
    "PASSWORD": os.environ.get("DATABASE_PASSWORD") or os.environ.get("MYSQLPASSWORD"),
    "HOST": os.environ.get("DATABASE_HOST") or os.environ.get("MYSQLHOST"),
    "PORT": os.environ.get("DATABASE_PORT") or os.environ.get("MYSQLPORT"),
}


def mysql_database_from_url(database_url):
    parsed = urlparse(database_url)
    if not parsed.scheme.startswith("mysql"):
        return None
    return {
        "ENGINE": "django.db.backends.mysql",
        "NAME": parsed.path.lstrip("/"),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or 3306),
    }


MYSQL_DATABASE_FROM_URL = mysql_database_from_url(DATABASE_URL) if DATABASE_URL else None

if not USE_SQLITE and MYSQL_DATABASE_FROM_URL:
    DATABASES = {"default": MYSQL_DATABASE_FROM_URL}
elif not USE_SQLITE and all(MYSQL_DATABASE.values()):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            **MYSQL_DATABASE,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ===== 비밀번호 검증 =====
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ===== 정적파일 =====
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# ===== API 키 =====
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

SERVICE_KEY = os.environ.get("SERVICE_KEY")
if not SERVICE_KEY:
    print("WARNING: SERVICE_KEY 환경 변수가 설정되지 않았습니다.")

# ===== Celery =====
CELERY_BROKER_URL = (
    os.environ.get("CELERY_BROKER_URL") or REDIS_CACHE_URL or "redis://localhost:6379/0"
)
CELERY_RESULT_BACKEND = (
    os.environ.get("CELERY_RESULT_BACKEND") or REDIS_CACHE_URL or "redis://localhost:6379/0"
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Seoul"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
