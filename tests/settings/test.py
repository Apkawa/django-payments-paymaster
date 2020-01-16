# coding: utf-8
from __future__ import unicode_literals

# noinspection PyUnresolvedReferences
from .dev import *


def _get_payment_host():
    from django.conf import settings
    return settings.LIVE_PAYMENT_HOST


PAYMENT_HOST = _get_payment_host
LIVE_PAYMENT_HOST = None
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TEST_ROOT, 'db_test.sqlite3'),
    }
}
