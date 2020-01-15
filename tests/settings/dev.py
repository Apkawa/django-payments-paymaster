import os
import sys

DEBUG = True
SITE_ID = 1

TEST_ROOT = os.path.normcase(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIXTURES_ROOT = os.path.join(TEST_ROOT, 'fixtures')

os.sys.path.insert(0, os.path.abspath(TEST_ROOT + '/../'))

MEDIA_ROOT = os.path.join(
    os.path.normcase(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'media')
MEDIA_URL = '/media/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(TEST_ROOT, 'templates')],
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

DATABASE_ENGINE = 'sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TEST_ROOT, 'db.sqlite3'),
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.admin',
    'payments',
    'tests',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

# This is only needed for the 1.4.X test environment
USE_TZ = True

SECRET_KEY = 'easy'

ROOT_URLCONF = 'tests.urls'

PAYMENT_HOST = 'localhost:8011'
PAYMENT_USES_SSL = False
PAYMENT_MODEL = 'payments_paymaster_tests.Payment'
PAYMENT_VARIANTS = {
    'default': ('payments.dummy.DummyProvider', {}),
    'paymaster': (
        'payments_paymaster.provider.PaymasterProvider',
        {
            'client_id': os.environ.get('PAYMASTER_CLIENT_ID'),
            'secret': os.environ.get('PAYMASTER_SECRET'),
            'api_login': os.environ.get('PAYMASTER_API_LOGIN'),
            'api_password': os.environ.get('PAYMASTER_API_PASS'),
        }
    )
}
