import logging
from logging.handlers import RotatingFileHandler

from superglot import create_app


if __name__ == '__main__':
    app = create_app()
    handler = RotatingFileHandler("log/error.log", maxBytes=10000000, backupCount=10)
    handler.setLevel(logging.WARNING)
    app.logger.addHandler(handler)
    app.run(debug=True, port=app.config['SERVER_PORT'])
