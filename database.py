
from flask import current_app as app

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)