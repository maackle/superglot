import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.login import UserMixin

import database as db

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

	id = sa.Column(sa.Integer, primary_key=True)  # TODO: composite key
	user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
	word_id = sa.Column(sa.Integer, sa.ForeignKey('word.id'))

	rating = sa.Column(sa.Integer)

	srs_data = sa.Column(JSON)

	word = relationship(Word)



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

	id = sa.Column(sa.Integer, primary_key=True)  # TODO: composite key
	article_id = sa.Column(sa.Integer, sa.ForeignKey('article.id', ondelete='CASCADE'))
	word_id = sa.Column(sa.Integer, sa.ForeignKey('word.id'))
	article_sentence_start = sa.Column(sa.Integer)  # a unique identifier for an article sentence
	# article_position = sa.Column(sa.Integer)
	
	article = relationship(Article, backref='word_occurrences')
