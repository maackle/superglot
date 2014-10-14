SECRET_KEY = '8ahsd7&&Gg9g7(*U![{S'

CSRF_ENABLED = True
WTF_CSRF_ENABLED = True

EMAIL_SUPPORT = 'support@superglot.com'

DEBUG = True

SERVER_PORT = 31337

NATIVE_LANGUAGES = ('en', 'es', 'it', 'ja')

TARGET_LANGUAGES = ('en',)

LANGUAGE_NAMES = {
	'en': 'English',
	'es': 'Español',
	'it': 'Italiano',
	'ja': '日本語',
}

SCORES = {
	'ignored': -1,
	'learning': 2,
	'known': 4,
}

NATIVE_LANGUAGE_CHOICES = tuple((code, LANGUAGE_NAMES[code]) for code in NATIVE_LANGUAGES)
TARGET_LANGUAGE_CHOICES = tuple((code, LANGUAGE_NAMES[code]) for code in TARGET_LANGUAGES)

DEBUG_TB_INTERCEPT_REDIRECTS = False

pwd = "v(4K9HUg9!sAba~"

import importlib
import os

try:
	mod = importlib.import_module(os.environ['SUPERGLOT_SETTINGS'])
	ldict = locals()
	for k in mod.__dict__:
	    if not k.startswith('__') or not k.endswith('__'):
	        ldict[k] = mod.__dict__[k]
except KeyError:
	from config.development import *