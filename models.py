import datetime
from collections import defaultdict

from flask import session, jsonify, current_app as app
from flask.ext.login import UserMixin
from mongoengine import *
from flask.ext.mongoengine import Document
from flask.ext.babel import lazy_gettext as _#, ngettext as __

from cache import cache
from decorators import memoized, lazyprop
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


	def __lt__(self, other):
		return self.reading.lower() < other.reading.lower()

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

	def __lt__(self, other):
		return self.word.reading.lower() < other.word.reading.lower()

	def __eq__(self, other):
		return self.word.id == other.word.id

	def __hash__(self):
		return util.string_hash(str(self.word.id))

	def __str__(self):
		return "[{}|{}]".format(self.word.reading, self.label)

	def __repr__(self):
		return self.__str__()


class AnnotatedDocWord():

	word = None
	label = None

	def __init__(self, word, label=None):
		self.word = word
		self.label = label

	def __lt__(self, other):
		return self.word.lemma < other.word.lemma

	def __eq__(self, other):
		return self.word.lemma == other.word.lemma

	def __hash__(self):
		return util.string_hash(str(self.word.lemma))

	def __str__(self):
		return "[{}|{}]".format(self.word.reading, self.label)

	def __repr__(self):
		return self.__str__()

VocabWord.sort_key = lambda v: v.word.lemma


class User(Document, UserMixin, CreationStamp):

	email = email_field()
	password = password_field()
	vocab = ListField(EmbeddedDocumentField(VocabWord))
	# target_languages = ListField(target_language_field())
	target_language = target_language_field()
	native_language = native_language_field()

	meta = {
		'index_options': {
			'unique': True,
			'dropDups': True,
			},
		'indexes': [
			'+vocab',
			]
	}

	def get_id(self):
		return str(self.id)

	@cache.memoize()
	def vocab_lists(self):
		partitions = defaultdict(set)
		for item in self.vocab:
			partitions[item.label].add(item.word)
		for label in partitions:
			partitions[label] = sorted(partitions[label])
		return partitions

	def words(self):
		for item in self.vocab:
			yield item.word

	def update_words(self, words, label):
		new_vocab = set(VocabWord(word=word, label=label) for word in words)
		self.vocab = list(new_vocab | set(self.vocab))
		self.save()
		cache.delete_memoized(self.vocab_lists)
		return True
	
	def delete_all_words(self):
		self.vocab = []
		self.save()
		cache.delete_memoized(self.vocab_lists)

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

	def word_stats(self, user):
		stats = {
			'counts': {},
			'percents': {},
			'total': 0,
		}

		total_marked = 0
		total_significant = 0

		for label, vocab_list in user.vocab_lists().items():
			num = len([word for word in vocab_list if (word in self.words)])
			stats['counts'][label] = num
			total_marked += num
			if label not in ('ignored',):
				total_significant += num


		total = len(set((w.lemma for w in self.words)))
		total_unmarked = total - total_marked
		divisor = total_significant + total_unmarked
		# total_significant = total_marked - stats['counts']['ignored']
			
		for label in user.vocab_lists().keys():
			if divisor == 0:
				percent = 0
			else:
				percent = float(100 * stats['counts'][label] / divisor)
			stats['percents'][label] = percent

		stats['total'] = total
		stats['total_significant'] = total_significant

		return stats


