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

RATING_VALUES = {
	'ignored': -1,
	'learning': 2,
	'known': 4,
}

def rating_name(rating):
	if rating == -1:
		return 'ignored'
	elif rating >= 0 and rating <= 2:
		return 'learning'
	elif rating <= 4:
		return 'known'
	else:
		return None

NATIVE_LANGUAGE_CHOICES = tuple((code, LANGUAGE_NAMES[code]) for code in SUPPORTED_NATIVE_LANGUAGES)
TARGET_LANGUAGE_CHOICES = tuple((code, LANGUAGE_NAMES[code]) for code in SUPPORTED_TARGET_LANGUAGES)

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