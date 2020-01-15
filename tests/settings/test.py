# coding: utf-8
from __future__ import unicode_literals

# noinspection PyUnresolvedReferences
from .dev import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
