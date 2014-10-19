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
import database as db
from config import settings


def load_schema_fixtures():
	languages = {}
	with db.session() as session:
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
	print('resetting schema for database {0}'.format(settings.DATABASE_NAME))
	db.engine.dispose()
	call('psql -c "DROP DATABASE {0};"'.format(settings.DATABASE_NAME), shell=True)
	call('psql -c "CREATE DATABASE {0};"'.format(settings.DATABASE_NAME), shell=True)
	call('psql -c "GRANT ALL ON DATABASE {0} TO {0};"'.format(settings.DATABASE_NAME), shell=True)
	models.Base.metadata.create_all(db.engine)
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
	call('psql -c "DROP DATABASE superglot_test;"', shell=True)
	call('psql -c "CREATE DATABASE superglot_test WITH TEMPLATE superglot_dev OWNER superglot_test;"', shell=True)


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