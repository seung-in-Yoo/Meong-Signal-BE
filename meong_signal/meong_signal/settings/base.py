"""
Django settings for meong_signal project.
Generated by 'django-admin startproject' using Django 5.0.6.
For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
import json
import os
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

secret_file = BASE_DIR / 'secrets.json'

with open(secret_file) as file:
    secrets = json.loads(file.read())

def get_secret(setting,secrets_dict = secrets):
    try:
        return secrets_dict[setting]
    except KeyError:
        error_msg = f'Set the {setting} environment variable'
        raise ImproperlyConfigured(error_msg)

SECRET_KEY = get_secret('SECRET_KEY') 
# s3
AWS_ACCESS_KEY_ID = get_secret('AWS_ACCESS_KEY_ID') 
AWS_SECRET_ACCESS_KEY = get_secret('AWS_SECRET_ACCESS_KEY')
AWS_REGION = 'ap-northeast-2'

# S3 Storages
AWS_STORAGE_BUCKET_NAME = get_secret('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (AWS_STORAGE_BUCKET_NAME,AWS_REGION)
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['meong-signal-back.p-e.kr', 'localhost', '127.0.0.1', 'msignal.kro.kr']


# Application definition

INSTALLED_APPS = [
    "account",
    "achievement",
    "dog",
    "review",
    "walk",
    #
    'corsheaders',
    'drf_yasg',
    'rest_framework',
    'rest_framework_simplejwt',
    'storages',
    #
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    #"django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'BearerAuth': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': "JWT Token"
        }
    },
    'SECURITY_REQUIREMENTS': [{
        'BearerAuth': []
    }]
}

CORS_ALLOW_METHODS = [  # 허용할 옵션
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [  # 허용할 헤더
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://meong-signal-back.p-e.kr",
    "https://meong-signal-back.p-e.kr",
    "http://msignal.kro.kr",
    "https://msignal.kro.kr"
]

ROOT_URLCONF = "meong_signal.urls"

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

WSGI_APPLICATION = "meong_signal.wsgi.application"

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',  # 인증된 요청인지 확인
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT를 통한 인증방식 사용
    ),
}

REST_USE_JWT = True
# JWT를 기본 인증 방식으로 사용하도록 설정

SIMPLE_JWT = {
    'SIGNING_KEY': SECRET_KEY, 
		# JWT에서 가장 중요한 인증키입니다! 
		# 이 키가 알려지게 되면 JWT의 인증체계가 다 털릴 수 있으니 노출되지 않게 조심해야합니다!
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
		# access token의 유효시간을 설정합니다.
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
		# refresh token의 유효시간을 설정합니다.
    'ROTATE_REFRESH_TOKENS': False,
		# True로 설정하면 리프레시 토큰이 사용될 때마다 새로운 리프레시 토큰이 발급됩니다.
    'BLACKLIST_AFTER_ROTATION': True,
		# 리프레시 토큰 회전 후, 이전의 리프레시 토큰이 블랙리스트에 추가될지 여부를 나타내는 부울 값입니다. 
		# True로 설정하면 리프레시 토큰이 회전되면서, 이전의 리프레시 토큰은 블랙리스트에 추가되어 더 이상 사용할 수 없게 됩니다.
}

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

AUTH_USER_MODEL = 'account.User'

AUTHENTICATION_BACKENDS = [
    'account.backends.EmailBackend',  # 커스텀 인증 백엔드
    'django.contrib.auth.backends.ModelBackend',

]

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR,'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"