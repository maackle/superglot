from database import db
from sqlalchemy.dialects.postgresql import JSON

Base = db.Model

class Language(Base):
	__tablename__ = 'language'

	id = db.Column(db.Integer, primary_key=True)
	code = db.Column(db.String(8))
	

class Word(Base):
	__tablename__ = 'word'

	id = db.Column(db.Integer, primary_key=True)
	lemma = db.Column(db.String(256), unique=True)
	language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
	canonical = db.Column(db.Boolean(), default=True)
	
	language = db.relationship(Language)

	def __str__(self):
		return "Word({})".format(self.lemma)



class LemmaReading(Base):
	__tablename__ = 'lemma_reading'

	id = db.Column(db.Integer, primary_key=True)
	lemma = db.Column(db.String(256))
	reading = db.Column(db.String(256))
	

class User(Base):
	__tablename__ = 'user'
	
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(256))
	password = db.Column(db.String(256))
	target_language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=True)
	native_language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=True)


class VocabWord(Base):
	__tablename__ = 'user_word'

	id = db.Column(db.Integer, primary_key=True)  # TODO: composite key
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	word_id = db.Column(db.Integer, db.ForeignKey('word.id'))



class Article(Base):
	__tablename__ = 'article'

	id = db.Column(db.Integer, primary_key=True)
	plaintext = db.Column(db.Text)
	sentence_positions = db.Column(JSON)

	user_id = db.Column(db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
	title = db.Column(db.String(256))
	source = db.Column(db.String(256), nullable=True)
	

class WordOccurrence(Base):
	__tablename__ = 'article_word'

	id = db.Column(db.Integer, primary_key=True)  # TODO: composite key
	article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'))
	word_id = db.Column(db.Integer, db.ForeignKey('word.id'))
	article_sentence_start = db.Column(db.Integer)  # a unique identifier for an article sentence
	# article_position = db.Column(db.Integer)
	
	article = db.relationship(Article, backref='word_occurrences')
