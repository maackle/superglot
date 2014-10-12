import mongoengine

import nlp

from flask.ext.sqlalchemy import SQLAlchemy
from application import create_app

app = create_app()
db = SQLAlchemy(app)

def setup_package():
	import superglot
	# db = mongoengine.connect('superglot_test')
	superglot.add_corncob_words()
	# with open('tests/fixtures/initial-words.txt', 'r') as infile:
	# 	db.drop_database('superglot_test')
	# 	def gen():
	# 		for line in infile:
	# 			reading = line.strip()
	# 			# yield models.Word(reading=reading, lemma=nlp.lemmatize_word(reading), language='en')
	# 			yield {
	# 				"reading": reading, "lemma": nlp.lemmatize_word(reading), "language": 'en',
	# 			}
	# 	models.Word._get_collection().insert(gen())
	# 	num = models.Word.objects.count()
	# 	print("{} words added".format(num))
