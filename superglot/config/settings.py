# flake8: noqa

SECRET_KEY = '8ahsd7&&Gg9g7(*U![{S'

CSRF_ENABLED = True
WTF_CSRF_ENABLED = True

EMAIL_SUPPORT = 'support@superglot.com'

DEBUG = True
DEVELOPMENT = False

SERVER_PORT = 31337

SUPPORTED_NATIVE_LANGUAGES = ('en', 'es', 'it', 'ja')

SUPPORTED_TARGET_LANGUAGES = ('en',)

LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Español',
    'it': 'Italiano',
    'ja': '日本語',
}

NATIVE_LANGUAGE_CHOICES = tuple(
    (code, LANGUAGE_NAMES[code]) for code in SUPPORTED_NATIVE_LANGUAGES)

TARGET_LANGUAGE_CHOICES = tuple(
    (code, LANGUAGE_NAMES[code]) for code in SUPPORTED_TARGET_LANGUAGES)

DEBUG_TB_INTERCEPT_REDIRECTS = False

SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = 'saltycookie'

pwd = "v(4K9HUg9!sAba~"

import importlib
import os
import logging
logger = logging.getLogger(__name__)

try:
    mod = importlib.import_module(os.environ['SUPERGLOT_SETTINGS'])
    ldict = locals()
    for k in mod.__dict__:
        if not k.startswith('__') or not k.endswith('__'):
            ldict[k] = mod.__dict__[k]
except KeyError:
    logger.warn("SUPERGLOT_SETTINGS not defined, not loading env settings")

try:
    from superglot.config.local import *
except:
    logger.warn("no local settings to import")
