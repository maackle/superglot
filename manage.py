import sys
from subprocess import call
from collections import defaultdict

from flask.ext.script import Manager, Command

from application import create_app

app = create_app()
manager = Manager(app)

import nlp
import textblob
from relational import models
import database
from config import settings


def load_schema_fixtures():
	languages = {}
	with database.session() as session:
		for i, code in enumerate(settings.SUPPORTED_NATIVE_LANGUAGES):
			language_id = i + 1
			languages[code] = models.Language(id=language_id, code=code)
			session.add(languages[code])
		user = models.User(email='michael@lv11.co', password='1234')
		session.add(user)
		session.commit()
	app.logger.info("schema fixtures created")


@manager.command
def reset_schema():
	dbname = settings.DATABASE_NAME
	print('resetting schema for database {0}'.format(dbname))
	database.engine.dispose()
	# call('psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = \'{0}\'"'.format(dbname), shell=True)
	# if call('psql -c "DROP DATABASE {0};"'.format(dbname), shell=True):
	# 	if call('dropdb {0}'.format(dbname)):
	# 		raise "Couldn't drop DB"
	# call('psql -c "CREATE DATABASE {0};"'.format(dbname), shell=True)
	# call('psql -c "GRANT ALL ON DATABASE {0} TO {0};"'.format(dbname), shell=True)
	call('bin/db-drop-create.sh {0}'.format(dbname), shell=True)
	print('building schema')
	models.Base.metadata.create_all(database.engine)
	load_schema_fixtures()


@manager.command
def load_fixture_words():
	import superglot
	superglot.add_fixture_words()


@manager.command
def rebuild_db():
	reset_schema()
	load_fixture_words()
	db.engine.dispose()

@manager.command
def translate(task, lang=None):
	potfile = 'translations/messages.pot'

	if task=='extract':
		call("pybabel extract -F config/babel.cfg -o {} .".format(potfile), shell=True)
	if task=='compile':
		call("pybabel compile -f -d translations", shell=True)
	if task=='update':
		call("pybabel update -i {} -d translations".format(potfile), shell=True)
	if task=='init':
		if not lang:
			raise Exception("missing language")
		call("pybabel init -i {} -d translations -l {}".format(potfile, lang), shell=True)


if __name__ == "__main__":
    manager.run()