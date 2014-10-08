MONGODB_SETTINGS = {
	'DB': 'superglot',
	# 'HOST': 'mongodb://superglot:superglot@ds027769.mongolab.com:27769/superglot'
}

SERVER_PORT = 31337
BASE_URL = 'http://localhost:{}/'.format(SERVER_PORT)
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/superglot_dev'