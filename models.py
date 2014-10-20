import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.login import UserMixin
from config import settings

import database as db
import util

Base = declarative_base()

class Language(Base):
	__tablename__ = 'language'

	id = sa.Column(sa.Integer, primary_key=True)
	code = sa.Column(sa.String(8), info={
		'choices': [('en', 'English')]
		})
	

class Word(Base):
	__tablename__ = 'word'

	id = sa.Column(sa.Integer, primary_key=True)
	lemma = sa.Column(sa.String(256), unique=True)
	language_id = sa.Column(sa.Integer, sa.ForeignKey('language.id'))
	canonical = sa.Column(sa.Boolean(), default=True)
	
	language = relationship(Language)

	def __str__(self):
		return "Word({})".format(self.lemma)

	def __eq__(self, other):
		return (self.id and self.id == other.id) or self.lemma == other.lemma

	def __hash__(self):
		return util.string_hash(self.lemma)


class LemmaReading(Base):
	__tablename__ = 'lemma_reading'

	id = sa.Column(sa.Integer, primary_key=True)
	lemma = sa.Column(sa.String(256))
	reading = sa.Column(sa.String(256))
	

class User(Base, UserMixin):
	__tablename__ = 'user'
	
	id = sa.Column(sa.Integer, primary_key=True)
	email = sa.Column(sa.String(256))
	password = sa.Column(sa.String(256))
	target_language_id = sa.Column(sa.Integer, sa.ForeignKey('language.id'), nullable=True)
	native_language_id = sa.Column(sa.Integer, sa.ForeignKey('language.id'), nullable=True)

	target_language = relationship(Language, foreign_keys=[target_language_id])
	native_language = relationship(Language, foreign_keys=[native_language_id])

	vocab = relationship('VocabWord', lazy='dynamic')

	def get_id(self):
		return str(self.id)


class VocabWord(Base):
	__tablename__ = 'user_word'
	__table_args__ = (
		sa.PrimaryKeyConstraint("user_id", "word_id"),
	)

	# id = sa.Column(sa.Integer, primary_key=True)  # TODO: composite key
	user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
	word_id = sa.Column(sa.Integer, sa.ForeignKey('word.id'), nullable=False)

	rating = sa.Column(sa.Integer)

	srs_next_repetition = sa.Column(sa.DateTime())
	srs_data = sa.Column(JSON)

	word = relationship(Word, cascade="all, delete", single_parent=True)
	user = relationship(User, cascade="all, delete", single_parent=True)

	@property
	def label(self):
		return settings.rating_name(self.rating)

	def __str__(self):
		return "VocabWord<{}>".format(self.word.lemma)

	def __lt__(self, other):
		return self.word.lemma < other.word.lemma



class Article(Base):
	__tablename__ = 'article'

	id = sa.Column(sa.Integer, primary_key=True)
	plaintext = sa.Column(sa.Text)
	sentence_positions = sa.Column(JSON)

	user_id = sa.Column(sa.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
	title = sa.Column(sa.String(256))
	source = sa.Column(sa.String(256), nullable=True)
	

class WordOccurrence(Base):
	__tablename__ = 'article_word'

	# id = sa.Column(sa.Integer, primary_key=True)  # TODO: composite key
	article_id = sa.Column(sa.Integer, sa.ForeignKey('article.id', ondelete='CASCADE'))
	word_id = sa.Column(sa.Integer, sa.ForeignKey('word.id'))
	article_sentence_start = sa.Column(sa.Integer)  # a unique identifier for an article sentence
	# article_position = sa.Column(sa.Integer)
	
	word = relationship(Word, backref='word_occurrences', cascade='delete')
	article = relationship(Article, backref='word_occurrences')


	__table_args__ = (
		sa.PrimaryKeyConstraint(article_id, word_id),
	)

	def __str__(self):
		return "WordOccurrence<{}>".format(self.word.lemma)
