MONGODB_SETTINGS = {
	'DB': 'superglot_test',
}

SERVER_PORT = 31338
BASE_URL = 'http://localhost:{}/'.format(SERVER_PORT)
TESTING = True

CSRF_ENABLED = False
WTF_CSRF_ENABLED = False

DATABASE_NAME = 'superglot_test'
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/{}'.format(DATABASE_NAME)
ES_INDEX = 'superglot_test'