import datetime

from flask import session, jsonify
from flask.ext.login import UserMixin
from mongoengine import *
from flask.ext.mongoengine import Document

from decorators import memoized

email_field = lambda: StringField(max_length=128, required=True)
password_field = lambda: StringField(max_length=32, required=True)

word_reading_field = lambda: StringField(max_length=128)
word_lemma_field = lambda: StringField(max_length=128)
word_language_field = lambda: StringField(max_length=8)

lemmata_field = lambda: SortedListField(StringField(max_length=256, unique=True))


class CreationStamp:

	date_created = DateTimeField(default=datetime.datetime.now())


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
	recognized = BooleanField(default=True)

	def pair(self):
		return (self.reading, self.lemma)

	def __eq__(self, other):
		return self.lemma == other.lemma  # and self.reading.lower() == other.reading.lower()

	def __str__(self):
		return "Word({})".format(self.reading)

Word.sort_key = lambda w: w.lemma

words_field = lambda: ListField(ReferenceField(Word))


class UserWordList(EmbeddedDocument):

	group_names = {'ignored', 'learning', 'known'}

	known = words_field()
	learning = words_field()
	ignored = words_field()

	def has_word(self, word):
		for name in self.group_names:
			if word in getattr(self, name):
				return True
		return False

	def sort(self):
		self.known.sort(key=Word.sort_key)
		self.learning.sort(key=Word.sort_key)
		self.ignored.sort(key=Word.sort_key)

	@staticmethod
	def default():
		return UserWordList(
			known=[],
			learning=[],
			ignored=[],
			)

	def __str__(self):
		return str({
			'known': self.known,
			'learning': self.learning,
			'ignored': self.ignored,
			})


class User(Document, UserMixin, CreationStamp):

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

	def get_lemmata(self):
		ret = {}
		for partition in self.words:
			ret[partition] = list(map(lambda x: x.lemma, self.words[partition]))
		return ret

	def json(self):
		return jsonify({
			'email': self.email,
			'lemmata': self.get_lemmata(),
		})

	def get_id(self):
		return str(self.id)

	def update_word(self, word, new_group_name):
		other_group_names = self.words.group_names - set(new_group_name)
		new_partition = getattr(self.words, new_group_name)
		old_group_name = None

		if word in new_partition:
			return None
		else:
			for group_name in other_group_names:
				old_partition = getattr(self.words, group_name)
				if word in old_partition:
					User.objects(id=self.id).update_one(**{
						"pull__words__{}".format(group_name): word.id
					})
					old_group_name = group_name

			User.objects(id=self.id).update_one(**{
				"add_to_set__words__{}".format(new_group_name): [word.id,]
			})
			self.reload()
			return (old_group_name, new_group_name)
			

	@staticmethod
	def authenticate(email, password):
		user = User.objects(email=email, password=password).first()
		return user


class TextArticle(Document, CreationStamp):
	
	title = StringField(max_length=256)
	plaintext = StringField()
	source = StringField()
	words = words_field()
	user = ReferenceField(User)
	date_modified = DateTimeField(default=datetime.datetime.now)

	def sorted_words(self):
		from util import sorted_words
		return sorted_words(self.words)

	def sorted_lemmata(self):
		return sorted(set(map(lambda x: x.lemma, self.words)), key=str.lower)

	def word_stats(self, wordlist):
		stats = {
			'counts': {},
			'percents': {},
			'total': len(self.words),
		}

		for name in UserWordList.group_names:
			group = getattr(wordlist, name)
			num = len([word for word in group if (word in self.words)])
			stats['counts'][name] = num
			stats['percents'][name] = float(100 * num / stats['total'])
		return stats



class WordOccurrence(Document):

	reading = word_reading_field()
	word = ReferenceField(Word)
	article = ReferenceField(TextArticle)
	position = IntField()

