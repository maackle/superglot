import mongoengine

import nlp
import models

def setup_package():
	db = mongoengine.connect('superglot_test')
	with open('tests/fixtures/initial-words.txt', 'r') as infile:
		db.drop_database('superglot_test')
		def gen():
			for line in infile:
				reading = line.strip()
				# yield models.Word(reading=reading, lemma=nlp.lemmatize_word(reading), language='en')
				yield {
					"reading": reading, "lemma": nlp.lemmatize_word(reading), "language": 'en',
				}
		models.Word._get_collection().insert(gen())
		num = models.Word.objects.count()
		print("{} words added".format(num))
