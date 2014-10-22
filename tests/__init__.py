import os
os.environ["SUPERGLOT_SETTINGS"] = 'config.testing'

import manage

def setup_sql_logging():
	import logging
	logging.basicConfig()
	logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def setup_package():
	import application
	app = application.create_app()
	with app.app_context():
		manage.rebuild_db()
