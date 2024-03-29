from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON

from flask.ext.security import UserMixin, RoleMixin, SQLAlchemyUserDatastore
from flask.ext.sqlalchemy import SQLAlchemy

from superglot import util

db = SQLAlchemy()


def query(*models):
    from flask import current_app
    return current_app.db.session.query(*models)


class Model(db.Model):
    __abstract__ = True

    @classmethod
    def query(cls):
        from flask import current_app
        return current_app.db.session.query(cls)


class Language(Model):
    __tablename__ = 'language'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), info={
        'choices': [('en', 'English')]
        })


class Word(Model):
    __tablename__ = 'word'

    id = db.Column(db.Integer, primary_key=True)
    lemma = db.Column(db.String(256), unique=True)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    canonical = db.Column(db.Boolean(), default=True)

    language = relationship(Language)

    def __repr__(self):
        return "<Word:{} {}>".format(self.id, self.lemma)

    def __eq__(self, other):
        return (self.id and self.id == other.id) or self.lemma == other.lemma

    def __hash__(self):
        return util.string_hash(self.lemma)


class LemmaReading(Model):
    __tablename__ = 'lemma_reading'

    id = db.Column(db.Integer, primary_key=True)
    lemma = db.Column(db.String(256))
    reading = db.Column(db.String(256))


# USER & AUTH -----------------------------------------------------------------


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    password = db.Column(db.String(256))

    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    target_language_id = db.Column(
        db.Integer, db.ForeignKey('language.id'), nullable=True)
    native_language_id = db.Column(
        db.Integer, db.ForeignKey('language.id'), nullable=True)

    target_language = relationship(Language, foreign_keys=[target_language_id])
    native_language = relationship(Language, foreign_keys=[native_language_id])

    vocab = relationship('VocabWord', lazy='dynamic')

    def get_id(self):
        return str(self.id)

    def __str__(self):
        return "<User: {}>".format(str(self.email))


user_datastore = SQLAlchemyUserDatastore(db, User, Role)


# ARTICLE & VOCAB -------------------------------------------------------------


class VocabWord(Model):
    __tablename__ = 'vocabword'
    __table_args__ = (
        db.PrimaryKeyConstraint("user_id", "word_id"),
    )

    # id = db.Column(db.Integer, primary_key=True)  # TODO: composite key
    user_id = db.Column(
        db.Integer, db.ForeignKey(
            'user.id', ondelete='CASCADE'
        ), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)

    rating = db.Column(db.Integer, default=0)

    srs_rating = db.Column(db.Integer, default=0)
    srs_last_rated = db.Column(db.DateTime(), default=util.now, nullable=False)
    srs_last_repetition = db.Column(
        db.DateTime(), default=util.now, nullable=False)
    srs_next_repetition = db.Column(
        db.DateTime(), default=util.now, nullable=False)
    srs_ease_factor = db.Column(db.Integer, default=1.4)
    srs_num_repetitions = db.Column(db.Integer, default=0)

    srs_data = db.Column(JSON, default={})

    # srs_score = IntField(default=0)
    # srs_ease_factor = DecimalField(default=2.5)
    # srs_num_repetitions = IntField(default=0)

    word = relationship(Word, cascade="all, delete", single_parent=True)
    user = relationship(User, cascade="all, delete", single_parent=True)

    def __str__(self):
        return "VocabWord<{}>".format(self.word.lemma)

    def __repr__(self):
        return "VocabWord<{}>".format(self.word.lemma)

    def __lt__(self, other):
        return self.word.lemma < other.word.lemma

    # def __eq__(self, other):
    #   return (self.user_id == other.user_id) and (self.word_id == other.word_id)

    # def __hash__(self):
    #   return util.string_hash(self.user_id + ' ' + self.word_id)


class VocabOccurrence(object):
    """ Not really a model, just a helper to unify VocabWord and Occurrence
        into a single object.

        On second thought maybe this isn't such a good
        idea :)
    """

    def __init__(self, vocab, occurrence):
        "todo"


class Article(Model):
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True)
    plaintext = db.Column(db.Text)
    sentence_positions = db.Column(JSON)
    # total_words = db.Column(db.Integer)

    user_id = db.Column(db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(256))
    source = db.Column(db.String(256), nullable=True)

    def __str__(self):
        return '<Article "{}" ({}...)>'.format(
            self.title,
            self.plaintext[0:40],
        )


class WordOccurrence(Model):
    __tablename__ = 'wordoccurrence'

    # id = db.Column(db.Integer, primary_key=True)  # TODO: composite key
    article_id = db.Column(db.Integer,
                           db.ForeignKey('article.id', ondelete='CASCADE'))
    word_id = db.Column(db.Integer,
                        db.ForeignKey('word.id', ondelete='CASCADE'))
    reading = db.Column(db.String(256))
    part_of_speech = db.Column(db.String(256), nullable=True)

    # a unique identifier for an article sentence
    article_sentence_start = db.Column(db.Integer, nullable=True)
    article_position = db.Column(db.Integer, nullable=True)

    word = relationship(Word,
                        backref='word_occurrences',
                        cascade="all, delete-orphan",
                        single_parent=True)
    article = relationship(Article,
                           backref='word_occurrences',
                           cascade="all, delete-orphan",
                           single_parent=True)

    __table_args__ = (
        db.PrimaryKeyConstraint(article_id, word_id, article_position),
    )

    def __str__(self):
        return "WordOccurrence<{} {}>".format(
            self.word.reading,
            self.article_position
        )

    def __repr__(self):
        return self.__str__()


class ArticleComputedStats(Model):
    __tablename__ = 'article_stats'

    user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'))
    article_id = db.Column(db.ForeignKey('article.id', ondelete='CASCADE'))

    stats = db.Column(JSON)

    __table_args__ = (
        db.PrimaryKeyConstraint(user_id, article_id),
    )
