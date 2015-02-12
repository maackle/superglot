import sys, os
from subprocess import call
from collections import defaultdict
import textblob

from flask.ext.script import Manager, Command

from superglot import create_app

app = create_app()
manager = Manager(app)

from superglot import nlp
from superglot import util
from superglot import models
from superglot import database
from superglot import core
from superglot import elasticsearch as es
from superglot.config import settings


dbname = settings.DATABASE_NAME


def psql(cmd):
    call("psql -c \"{}\"".format(cmd), shell=True)


def dumpfile(dbname):
    return "dump/{0}.sql".format(dbname)


def load_schema_fixtures():
    languages = {}
    with database.session() as session:
        for i, code in enumerate(settings.SUPPORTED_NATIVE_LANGUAGES):
            language_id = i + 1
            languages[code] = models.Language(id=language_id, code=code)
            session.add(languages[code])
        session.commit()
    app.logger.info("schema fixtures created")


def load_sample_data():
    user = models.User(email='michael@lv11.co', password='1234')
    app.db.session.add(user)
    app.db.session.commit()
    article, created = core.create_article(
        user=user,
        title='Sample Text',
        plaintext="""
This is a sample text. Hope you enjoy it.
            """
    )


def db_drop_create():
    call('bin/db-drop-create.sh {0}'.format(dbname), shell=True)
    database.engine.dispose()


@manager.command
def make_dump():
    filename = dumpfile(settings.DATABASE_NAME)
    print("writing PG dump to {}".format(filename))
    call("pg_dump -i -F c -f {1} {0}".format(settings.DATABASE_NAME, filename), shell=True)


@manager.command
def load_dump():
    filename = dumpfile(settings.DATABASE_NAME)
    print("reading PG dump {0}".format(filename))
    call("pg_restore -i -d {0} {1}".format(settings.DATABASE_NAME, filename), shell=True)


@manager.command
def reset_schema():
    dbname = settings.DATABASE_NAME
    print('resetting schema for database {0}'.format(dbname))
    db_drop_create()
    print('building schema')
    models.Base.metadata.create_all(database.engine)
    load_schema_fixtures()


@manager.command
def load_fixture_words(filename='data/en-2000.txt'):
    from collections import defaultdict
    import textblob
    from superglot import database

    english_id = 1

    with open(filename, 'r') as f:
        lines = list(f)
        items = []
        words = defaultdict(list)
        for reading in lines:
            reading = reading.strip()
            tw = textblob.Word(reading)
            lemmata = set()
            lemmata.add(tw.lemmatize('n'))
            lemmata.add(tw.lemmatize('v'))
            lemmata.add(tw.lemmatize('a'))  # adj
            lemmata.add(tw.lemmatize('r'))  # adv
            for lemma in lemmata:
                words[lemma].append(reading)

        database.engine.execute(models.Word.__table__.insert(),
            [{
                'lemma': lemma,
                'language_id': english_id,
            } for lemma in words.keys()])

        rows = []
        for lemma, readings in words.items():
            for reading in readings:
                rows.append({
                    'lemma': lemma,
                    'reading': reading,
                })
        database.engine.execute(models.LemmaReading.__table__.insert(), rows)
    app.logger.info("corncob readings added")


@manager.command
def rebuild_db(force=False):
    if not force and os.path.isfile(dumpfile(settings.DATABASE_NAME)):
        db_drop_create()
        load_dump()
    else:
        reset_schema()
        # load_fixture_words()
        if settings.DEVELOPMENT:
            load_sample_data()
        database.engine.dispose()
        make_dump()


@manager.command
def translate(task, lang=None):
    potfile = 'translations/messages.pot'

    if task=='extract':
        call("pybabel extract -F config/babel.cfg -o {} .".format(potfile), shell=True)
    if task=='compile':
        call("pybabel compile -f -d translations", shell=True)
    if task=='update':
        call("pybabel update -i {} -d translations".format(potfile), shell=True)
    if task=='init':
        if not lang:
            raise Exception("missing language")
        call("pybabel init -i {} -d translations -l {}".format(potfile, lang), shell=True)


@manager.command
def sync_es():
    es.rebuild_index(app.es)
    print("ES index rebuilt")


@manager.command
def create_test_data():

    test_articles = [
        {
            'file': 'data/articles/game-for-fools.txt',
            'title': 'The Game For Fools',
        },
        {
            'file': 'data/articles/little-prince-1.txt',
            'title': 'The Little Prince Ch. 1',
        },
        {
            'file': 'data/articles/little-prince-2.txt',
            'title': 'The Little Prince Ch. 2',
        },
        {
            'file': 'data/articles/moby-dick-1.txt',
            'title': 'Moby Dick Ch. 1',
        },
        # {
        #   'file': 'data/articles/moby-dick-full.txt',
        #   'title': 'Moby Dick (Full)',
        # },
    ]

    test_users = []
    for i in range(1,4):
        u, created = core.register_user('{}@test.com'.format(i), str(i))
        test_users.append(u)

    def _create_article(user, article_def):
        with open(article_def['file'], 'r') as f:
            plaintext = f.read()
            with util.Timer() as t:
                article, created = core.create_article(
                    user=user,
                    title=article_def['title'],
                    plaintext=plaintext[0:]
                )
            print("created '{}' (length: {}) in {} ms".format(
                article.title,
                len(article.plaintext),
                t.msecs
            ))
        return article, created

    for i, article_def in enumerate(test_articles):
        user_index = i % len(test_users)
        article, created = _create_article(test_users[user_index], article_def)
    sync_es()

if __name__ == "__main__":
    manager.run()