import datetime

from flask import session
from flask.ext.login import UserMixin
from mongoengine import *
from flask.ext.mongoengine import Document
email_field = lambda: StringField(max_length=128, required=True)
password_field = lambda: StringField(max_length=32, required=True)

word_reading_field = lambda: StringField(max_length=128)
word_lemma_field = lambda: StringField(max_length=128)
word_language_field = lambda: StringField(max_length=8)

lemmata_field = lambda: SortedListField(StringField(max_length=256, unique=True))

# class UserLemmaList(EmbeddedDocument):

# 	known = lemmata_field()
# 	learning = lemmata_field()
# 	ignored = lemmata_field()

# 	def __str__(self):
# 		return str({
# 			'known': self.known,
# 			'learning': self.learning,
# 			'ignored': self.ignored,
# 			})


class Word(Document):

	meta = {
		# 'index_options': {
		# 	'unique': True,
		# 	'dropDups': True,
		# 	},
		'indexes': [ {
			'unique': True,
			'fields': ('reading',  'lemma',  'language'),
		}]
	}

	reading = word_reading_field()
	lemma = word_lemma_field()
	language = word_language_field()

	def __str__(self):
		return "Word({})".format(self.reading)

words_field = lambda: ListField(ReferenceField(Word))

class UserWordList(EmbeddedDocument):

	known = words_field()
	learning = words_field()
	ignored = words_field()

	def __str__(self):
		return str({
			'known': self.known,
			'learning': self.learning,
			'ignored': self.ignored,
			})


class User(Document, UserMixin):

	email = email_field()
	password = password_field()
	words = EmbeddedDocumentField(UserWordList)

	meta = {
		'index_options': {
			'unique': True,
			'dropDups': True,
			},
		'indexes': [
			'+words.known', 
			'+words.learning', 
			'+words.ignored',
			]
		# 'indexes': [
		# 	{'unique': True, 'fields': ['+words.known'] }, 
		# 	{'unique': True, 'fields': ['+words.learning'] }, 
		# 	{'unique': True, 'fields': ['+words.ignored'] },
		# 	]
	}


	def get_id(self):
		return str(self.id)

	@staticmethod
	def authenticate(email, password):
		user = User.objects(email=email, password=password).first()
		return user


class TextArticle(Document):
	
	title = StringField(max_length=256)
	plaintext = StringField()
	source = StringField()
	words = words_field()
	user = ReferenceField(User)
	date_modified = DateTimeField(default=datetime.datetime.now)

	def sorted_words(self):
		return sorted(self.words, key=lambda word: word.reading.lower())

	def sorted_lemmata(self):
		return sorted(set(map(lambda x: x.lemma, self.words)), key=str.lower)


class WordOccurrence(Document):

	reading = word_reading_field()
	word = ReferenceField(Word)
	article = ReferenceField(TextArticle)
	position = IntField()

