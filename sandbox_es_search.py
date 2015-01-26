import random

from superglot import models
from superglot import core
from superglot import elasticsearch
from superglot import database
from superglot import util

from pprint import pprint

from superglot import create_app

app = create_app()

def make_random_user():
    username = util.random_string(4)
    user, created = core.register_user(username, username)
    return user

def make_random_articles(user):
    num_user = 1000
    num_other = 10000
    num_repeats = 100
    user_lemmata = []
    other_lemmata = []
    for i in range(1, num_user):
        user_lemmata.append(util.random_string(8))
    for i in range(1, num_other):
        other_lemmata.append(util.random_string(8))
    core.make_words_from_lemmata(user_lemmata)
    core.make_words_from_lemmata(other_lemmata)
    user_lemmata_chunks = util.chunks(
        user_lemmata,
        int(len(user_lemmata) / 4),
    )
    user_lemmata_by_rating = {}
    for i, chunk in enumerate(user_lemmata_chunks):
        rating = i + 1
        lemmata = list(chunk)
        core.update_user_lemmata(user, lemmata, rating)
        user_lemmata_by_rating[rating] = chunk

    for rating, lemmata in user_lemmata_by_rating.items():
        random.shuffle(other_lemmata)
        selection = int(num_other/10)
        plaintext = " ".join(lemmata)
        plaintext += " ".join(other_lemmata[0:selection])
        for i in range(0, num_repeats):
            article, created = core.create_article(
                user=user,
                title='{} : {}'.format(user.email, rating),
                plaintext=plaintext,
            )
        print(article, len(article.plaintext))


def run():

    with app.app_context():

        user = make_random_user()
        make_random_articles(user)
        elasticsearch.rebuild_index(app.es)
        # user = session.query(models.User).first()

        vocab_string = " ".join(
            (w.word.lemma for w in user.vocab)
        )

        shoulds = [
            {
                'match': {
                    'plaintext': {
                        'query': w.word.lemma,
                        'boost': 5 - w.rating,
                    }
                }
            } for w in user.vocab]

        es = app.es
        print("starting search...")
        print("- {} search terms".format(len(shoulds)))
        try:
            print("- {} total articles".format(
                models.Article.query().count()
            ))
        except:
            pass
        with util.Timer() as t:
            results = es.search('superglot_dev', 'article', {
                'query': {
                    'bool': {
                        # 'must': {
                        #   'term': {
                        #       'user_id': user.id,
                        #   }
                        # },
                        'should': shoulds
                    }
                }
            })
        print("search done in {} ms".format(t.msecs))

        for r in results['hits']['hits']:
            print(r['_score'], "\t", r['_source']['title'])


if __name__ == '__main__':
    run()