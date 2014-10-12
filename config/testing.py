MONGODB_SETTINGS = {
	'DB': 'superglot_test',
}

SERVER_PORT = 31338
BASE_URL = 'http://localhost:{}/'.format(SERVER_PORT)
TESTING = True

CSRF_ENABLED = False
WTF_CSRF_ENABLED = False

SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/superglot_test'