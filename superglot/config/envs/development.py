DEVELOPMENT = True

SERVER_PORT = 31337
BASE_URL = 'http://localhost:{}/'.format(SERVER_PORT)

DATABASE_NAME = 'superglot_dev'
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/{}'.format(DATABASE_NAME)
ES_INDEX = 'superglot_dev'
