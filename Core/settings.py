from pathlib import Path
import os
import shutil
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ============ تحميل ملف .env (الأسرار) ============
_env_file = BASE_DIR / '.env'
if _env_file.exists():
    for _line in _env_file.read_text(encoding='utf-8').splitlines():
        _line = _line.strip()
        if _line and not _line.startswith('#') and '=' in _line:
            _key, _, _value = _line.partition('=')
            os.environ.setdefault(_key.strip(), _value.strip().strip('"').strip("'"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['.vercel.app', '127.0.0.1', 'localhost', '*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    # Cloudinary storage apps
    'cloudinary_storage',
    'cloudinary',
    
    'django.contrib.staticfiles',
    'store', # تطبيق المتجر/الأعمال الخاص بك
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # تفعيل WhiteNoise لخدمة الملفات الثابتة على Vercel
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # المجلد الرئيسي الذي يحتوي على index.html
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'Core.wsgi.application'

# ============ Database Setup (Neon PostgreSQL / SQLite Fallback) ============
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    ORIGINAL_DB = BASE_DIR / 'db.sqlite3'
    TMP_DB = Path('/tmp/db.sqlite3')

    if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
        if ORIGINAL_DB.exists() and not TMP_DB.exists():
            shutil.copyfile(ORIGINAL_DB, TMP_DB)
            os.chmod(TMP_DB, 0o666)
        DB_PATH = TMP_DB
    else:
        DB_PATH = ORIGINAL_DB

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': DB_PATH,
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'staticfiles'] 
STATIC_ROOT = BASE_DIR / "static_root"

# Media files (Uploaded images for projects)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ============ Cloudinary Storage Config ============
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'xelbohhj'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', '381188723524369'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

# إعداد خزن الملفات الثابتة والصور عبر Cloudinary & WhiteNoise
STORAGES = {
    "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# ============ مفاتيح الـ API والخدمات الخارجية ============
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
AI_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')

# ============ إعدادات الجلسات (Sessions) ============
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True