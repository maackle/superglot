import sys
from flask.ext.script import Manager

from application import app, db
from models import User
import nlp

manager = Manager(app)

@manager.command
def populate():
	with open('data/corncob_words.txt', 'r') as infile:
		db.words.drop()
		for i, line in enumerate(infile):
			word = line.strip()
			db.words.insert({
				'reading': word,
				'lemma': nlp.lemmatize_word(word),  # TODO: can't do POS-enabled lemmatize here, so what?
				'language': 'en',
			})
			if (i % 1000) == 0:
				print('.', end='')
				sys.stdout.flush()
		num = db.words.count()
		app.logger.info("{} words added".format(num))


@manager.command
def edit_user():
	data = db.users.find_one({'email': 'maackle.d@gmail.com'})
	michael = User(**data)
	michael.password = 'asdf'
	michael.save()

if __name__ == "__main__":
    manager.run()