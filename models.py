import datetime

from flask import session, jsonify, current_app as app
from flask.ext.login import UserMixin
from mongoengine import *
from flask.ext.mongoengine import Document
from flask.ext.babel import lazy_gettext as _#, ngettext as __

from decorators import memoized
import util
import nlp
from config import settings

email_field = lambda: StringField(max_length=128, required=True, verbose_name=_('email').capitalize())
password_field = lambda: StringField(max_length=32, required=True, verbose_name=_('password').capitalize())

word_reading_field = lambda: StringField(max_length=128, verbose_name=_('reading'))
word_lemma_field = lambda: StringField(max_length=128, verbose_name=_('lemma'))
native_language_field = lambda: StringField(max_length=8, verbose_name=_('native language').capitalize(), default="en", choices=settings.NATIVE_LANGUAGE_CHOICES)
target_language_field = lambda: StringField(max_length=8, verbose_name=_('target language').capitalize(), default="en", choices=settings.TARGET_LANGUAGE_CHOICES)

lemmata_field = lambda: SortedListField(StringField(max_length=256, unique=True))


class CreationStamp:

	date_created = DateTimeField(default=datetime.datetime.now())


class WordMeaning(EmbeddedDocument):
	language = StringField(max_length=8, required=True)
	meaning = StringField(max_length=256, required=True)


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
	language = native_language_field()
	meanings = MapField(EmbeddedDocumentField(WordMeaning))
	recognized = BooleanField(default=True)

	def pair(self):
		return (self.reading, self.lemma)

	def lookup(self, language):
		if language in self.meanings:
			print(language)
			return self.meanings[language]
		else:
			text = nlp.translate_word(self.reading, language)
			meaning = self.meanings[language] = WordMeaning(language=language, meaning=text)
			self.save()
			return meaning

	def __eq__(self, other):
		return self.language == other.language and self.lemma == other.lemma and self.reading.lower() == other.reading.lower()

	def __hash__(self):
		return util.string_hash(self.lemma + self.reading)

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
		'''
		Default user word list.
		NOTE that the ignored words must already exist in the DB to be added.
		'''
		ignored_lemmata = []
		with open('config/ignored-en.txt') as f:
			for line in f.readlines():
				lemma = line.strip()
				ignored_lemmata.append(lemma)

		ignored_words = Word.objects(lemma__in=ignored_lemmata)

		return UserWordList(
			known=[],
			learning=[],
			ignored=ignored_words,
			)

	def __str__(self):
		return str({
			'known': self.known,
			'learning': self.learning,
			'ignored': self.ignored,
			})


class VocabWord(EmbeddedDocument):

	word = ReferenceField(Word)
	label = StringField()


class User(Document, UserMixin, CreationStamp):

	email = email_field()
	password = password_field()
	vocabulary = ListField(EmbeddedDocumentField(VocabWord))
	words = EmbeddedDocumentField(UserWordList)
	# target_languages = ListField(target_language_field())
	target_language = target_language_field()
	native_language = native_language_field()

	meta = {
		'index_options': {
			'unique': True,
			'dropDups': True,
			},
		'indexes': [
			'+words.known', 
			'+words.learning', 
			'+words.ignored',
			'+vocabulary',
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


class WordOccurrence(EmbeddedDocument):

	word = ReferenceField(Word)
	locations = ListField(IntField())
	sentences = ListField(IntField())
	# reading = word_reading_field()
	# article = ReferenceField(TextArticle)


class TextArticle(Document, CreationStamp):
	
	title = StringField(max_length=256, verbose_name=_('title'))
	plaintext = StringField(verbose_name=_('plaintext'))
	source = StringField(verbose_name=_('source'))
	words = words_field()
	user = ReferenceField(User)
	occurrences = ListField(EmbeddedDocumentField(WordOccurrence))
	sentence_positions = ListField(ListField(IntField()))  # list of doubles
	date_modified = DateTimeField(default=datetime.datetime.now)

	def sentence(self, index):
		a,b = self.sentence_positions[index]
		return self.plaintext[a:b]

	def sorted_words(self):
		from util import sorted_words
		return sorted_words(self.words)

	def sorted_lemmata(self):
		return sorted(set(map(lambda x: x.lemma, self.words)), key=str.lower)

	def word_stats(self, wordlist):
		stats = {
			'counts': {},
			'percents': {},
			'total': 0,
		}

		total_marked = 0
		total_significant = 0
		group_names = UserWordList.group_names# - {'ignored'}

		for name in group_names:
			group = getattr(wordlist, name)
			num = len([word for word in group if (word in self.words)])
			stats['counts'][name] = num
			total_marked += num
			if name not in ('ignored',):
				total_significant += num


		total = len(set((w.lemma for w in self.words)))
		total_unmarked = total - total_marked
		divisor = total_significant + total_unmarked
		# total_significant = total_marked - stats['counts']['ignored']
			
		for name in group_names:
			if divisor == 0:
				percent = 0
			else:
				percent = float(100 * stats['counts'][name] / divisor)
			stats['percents'][name] = percent

		stats['total'] = total
		stats['total_significant'] = total_significant

		return stats


