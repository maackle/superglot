DEVELOPMENT = False

SERVER_PORT = 6107
BASE_URL = 'http://localhost:{}/'.format(SERVER_PORT)

DATABASE_NAME = 'superglot_dev'
SQLALCHEMY_DATABASE_URI = 'superglot_dev:superglot_dev@postgresql://localhost/{}'.format(DATABASE_NAME)
ES_INDEX = 'superglot_dev'
