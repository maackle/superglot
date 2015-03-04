DEBUG = True
LOAD_SAMPLE_DATA = True

SERVER_PORT = 6107
BASE_URL = 'http://localhost:{}/'.format(SERVER_PORT)

DATABASE_NAME = 'superglot_dev'
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/{}'.format(DATABASE_NAME)
ES_INDEX = 'superglot_dev'
