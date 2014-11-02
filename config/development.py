MONGODB_SETTINGS = {
	'DB': 'superglot',
	# 'HOST': 'mongodb://superglot:superglot@ds027769.mongolab.com:27769/superglot'
}

DEVELOPMENT = True

SERVER_PORT = 31337
BASE_URL = 'http://localhost:{}/'.format(SERVER_PORT)

DATABASE_NAME = 'superglot_dev'
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/{}'.format(DATABASE_NAME)
ES_INDEX = 'superglot_dev'