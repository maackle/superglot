import sys
from subprocess import call
from collections import defaultdict

from flask.ext.script import Manager, Command

from application import create_app
from models import User
import nlp
import textblob
import superglot

app = create_app()
manager = Manager(app)

@manager.command
def reset_schema():
	from database import db
	from relational.models import User

	call('psql -c "DROP DATABASE superglot_dev;"', shell=True)
	call('psql -c "CREATE DATABASE superglot_dev;"', shell=True)
	call('psql -c "GRANT ALL ON DATABASE superglot_dev TO superglot_dev;"', shell=True)
	db.create_all()

@manager.command
def schema_fixtures():
	from database import db
	from relational import models

	languages = {}
	for code in ('en', 'it', 'ja',):
		languages[code] = models.Language(code=code)
		db.session.add(languages[code])
	db.session.commit()

	user = models.User(email='michael@lv11.co', password='1234')
	db.session.add(user)
	db.session.commit()
	app.logger.info("schema fixtures created")

@manager.command
def fixture_words():
	superglot.add_corncob_words()


@manager.command
def rebuild_db():
	from database import db
	from relational.models import User

	reset_schema()
	schema_fixtures()
	fixture_words()


@manager.command
def edit_user():
	data = db.users.find_one({'email': 'maackle.d@gmail.com'})
	michael = User(**data)
	michael.password = 'asdf'
	michael.save()

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

# class Translate(Command):

# 	def run(self):
# 		pass

if __name__ == "__main__":
    manager.run()