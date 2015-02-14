'''
Complex queries, calculations, etc.
'''

import datetime
from collections import defaultdict

from sqlalchemy import distinct
from flask import current_app as app
from bs4 import BeautifulSoup

from superglot.cache import cache
from superglot.config import settings
from superglot import (
    nlp,
    util,
    models,
    database,
    srs,
)

try:
    with database.session() as session:
        english = session.query(models.Language).filter_by(code='en').first()
        english_id = english.id
except:
    print("WARNING: tried to access Language model without schema")
    english = None
    english_id = None

def add_word(session, reading, lemma, language=english):
    word = models.Word(lemma=lemma, language_id=english_id, canonical=False)
    session.add(word)
    session.add(models.LemmaReading(lemma=lemma, reading=reading))
    return word

def fetch_remote_article(url):
    ignored_tags = ['script', 'style', 'code', 'head', 'iframe']
    req = util.get_page(url)
    soup = BeautifulSoup(req.text)

    # remove noisy content-empty tags
    for tag in ignored_tags:
        for t in soup(tag):
            t.decompose()

    strings = (soup.stripped_strings)
    strings = (map(lambda x: re.sub(r"\s+", ' ', x), strings))
    plaintext = "\n".join(strings)
    return (plaintext, soup.title)

def gen_due_vocab(user):
    '''
    Get VocabWords that are due for study for this user
    '''

    return (item for item in user.vocab.all()
        if item.rating >= srs.RATING_MIN
        and item.srs_next_repetition
        and item.srs_next_repetition < util.now()
    )


def _get_common_vocab_query(user, article):
    '''
    Get VocabWords in the article
    '''

    V = models.VocabWord
    O = models.WordOccurrence
    return (
        app.db.session.query(V).
        join(O, V.word_id == O.word_id).
        filter(O.article_id == article.id).
        filter(V.user_id == user.id)
    )


# @cache.memoize()
def get_common_vocab(user, article):
    '''
    Get VocabWords in the article
    '''

    return _get_common_vocab_query(user, article).all()


# @cache.memoize()
def _get_common_vocab_pairs_query(user, article):
    '''
    Get vocab that show up in user's vocab and the article, paired with
    the occurrence of each vocab word
    '''

    V = models.VocabWord
    O = models.WordOccurrence
    return (
        app.db.session.query(V, O)
        .filter(O.article_id == article.id)
        .filter(V.word_id == O.word_id)
        .filter(V.user_id == user.id)
    )


# @cache.memoize()
def get_common_vocab_pairs(user, article):
    '''
    Get vocab that show up in user's vocab and the article, paired with
    the occurrence of each vocab word
    '''

    return _get_common_vocab_pairs_query(user, article).all()


# @cache.memoize()
def get_common_word_ids(user, article):
    '''
    Get Words in the article
    '''

    V = models.VocabWord
    return (v[0] for v in _get_common_vocab_query(user, article).values(V.word_id))


def gen_words_from_readings(readings):
    '''
    Look up words from token objects. If not in database, create a "non-canonical" word

    TODO: actually create the non-canonical word.
    '''
    lemma_readings = defaultdict(set)

    for reading in readings:
        for lemma in nlp.get_reading_lemmata(reading):
            lemma_readings[lemma].add(reading)
            app.db.session.add(models.LemmaReading(lemma=lemma, reading=reading))
    app.db.session.commit()

    for chunk in util.chunked(lemma_readings.items(), 500):
        words = []
        new_words = []
        for lemma, reading in chunk:
            word = app.db.session.query(models.Word).filter_by(
                lemma=lemma,
                language_id=english_id
            ).first()
            if not word:
                word = models.Word(
                    lemma=lemma,
                    language_id=english_id,
                    canonical=False
                )
                new_words.append(word)
            words.append(word)

        app.db.session.add_all(new_words)
        app.db.session.commit()

        for word in (words):
            yield word


def create_article(user, title, plaintext, url=None):
    '''
        TODO: save word position as well.
    '''
    all_tokens = list()

    sentence_positions = {}
    occurrences = []
    all_word_ids = set()
    for reading, span in nlp.tokenize_with_spans(plaintext):
        raise "TODO"
    for i, sentence in enumerate(nlp.get_sentences(plaintext)):
        sentence_positions[sentence.start] = len(sentence)
        sentence_tokens = nlp.tokenize(sentence.string)
        for token, word in zip(sentence_tokens, gen_words_from_tokens(sentence_tokens)):
            if word.id:
                occurrence = models.WordOccurrence(
                    word_id=word.id,
                    reading=token.reading,
                    article_sentence_start=sentence.start
                )
                occurrences.append(occurrence)
                all_word_ids.add(word.id)
        all_tokens.extend(sentence_tokens)

    article = models.Article(
        source=url,
        user_id=user.id,
        title=title,
        plaintext=plaintext,
        sentence_positions=sentence_positions,
    )

    app.db.session.add(article)
    app.db.session.commit()

    for o in occurrences:
        o.article_id = article.id
        app.db.session.merge(o)
    app.db.session.commit()

    existing_vocab_word_ids = set(get_common_word_ids(user, article))

    for word_id in all_word_ids - existing_vocab_word_ids:
        app.db.session.add(models.VocabWord(user_id=user.id, word_id=word_id, rating=0))
    app.db.session.commit()

    # cache.delete_memoized(get_common_word_pairs, user=user, article=article)

    return article, True


def vocab_stats(vocab):
    """ Get stats about a particular vocabulary list
    """
    counts = defaultdict(int)
    percents = defaultdict(int)

    for item in vocab:
        counts[item.rating] += 1

    total = len(vocab)
    total_significant = total - counts['ignored']

    for rating in counts:
        percents[rating] = 100 * counts[rating] / (total_significant or 1)

    return {
        'counts': counts,
        'percents': percents,
        'total_significant': total_significant,
        'total': total,
    }


def user_article_stats(user, article):
    """ Get stats about the common vocab between a user and an article
    """

    common = get_common_vocab(user, article)
    return vocab_stats(common)


def authenticate_user(email, password):
    # with database.session() as session:
    user = app.db.session.query(models.User).filter_by(email=email, password=password).first()
    return user


def register_user(email, password):
    session = app.db.session
    user = session.query(models.User).filter_by(email=email).first()
    if user:
        created = False
    else:
        user = models.User(email=email, password=password)
        session.add(user)
        session.commit()
        created = True
    return (user, created)


def _record_rating(vocab_word, rating):
    stats = srs.process_answer(
        rating,
        float(vocab_word.srs_ease_factor),
        vocab_word.srs_num_repetitions
    )
    interval, ease_factor, num_repetitions = stats
    # interval = 1
    vocab_word.srs_rating = rating
    vocab_word.srs_last_repetition = util.now()
    vocab_word.srs_next_repetition = util.now() + datetime.timedelta(days=interval)
    vocab_word.srs_ease_factor = ease_factor
    vocab_word.srs_num_repetitions = num_repetitions


def update_user_words(user, words, rating, force=False):
    updated = 0
    ignored = 0
    num_recorded = 0
    updated_vocab = []
    for word in set(words):
        if word.id or force:
            if force:
                app.db.session.add(word)
                app.db.session.commit()
            vocab_word = app.db.session.merge(models.VocabWord(
                user_id=user.id,
                word_id=word.id,
                rating=rating,
                srs_last_rated=util.now(),
            ))
            updated_vocab.append(vocab_word)
            updated += 1
        else:
            ignored += 1
    app.db.session.commit()
    for v in updated_vocab:
        if v.srs_next_repetition < util.now():
            num_recorded += 1
            _record_rating(v, rating)
            app.db.session.merge(v)
    app.db.session.commit()
    return updated, ignored


def update_user_lemmata(user, lemmata, rating):
    words = gen_words_from_lemmata(lemmata)
    return update_user_words(user, words, rating)


#############################################################

def get_article_sentences(article, words):
    '''Get all sentences that contain these words'''

    indices = """
    SELECT sentence_start from word_occurrence
    WHERE word_id IN ({word_ids}) AND article_id = {article.id}
    """

    O = models.WordOccurrence
    word_ids = list(w.id for w in words)
    sentence_starts = set(map(lambda r: r[0], (O.query()
        .filter(O.word_id.in_(word_ids))
        .values(O.article_sentence_start)
    )))
    sentences = list()
    for start in sentence_starts:
        # unfortunately PG JSON keys are strings...
        length = article.sentence_positions.get(str(start))
        if length:
            sentence_text = article.plaintext[start:start+length].strip()
            sentences.append(sentence_text)
    return sentences

def compute_article_stats(user, article):
    vocab = get_common_vocab(user, article)
    groups = util.multi_dict_from_seq(vocab, lambda v: v.rating)
    from pprint import pprint
    pprint(groups)

def find_all_articles(user):

    results = app.es.search(settings.ES_INDEX, 'article', {
        # 'sort': [
        #   '_score',
        # ],
    }, size=1000000)
    hits = results['hits']['hits']
    articles = [(h['_source'], h['_score']) for h in hits]
    return articles

def find_relevant_articles(user):

    vocab_string = " ".join([w.word.lemma for w in user.vocab])
    shoulds = [{
        'match': {'plaintext': v.word.lemma}
    } for v in user.vocab if v.rating > 0]

    results = app.es.search(settings.ES_INDEX, 'article', {
        'query': {
            'filtered': {
                'query': {
                    'bool': {
                        'should': shoulds
                    }
                },
                # 'filter': {
                #   'limit': {'value': 2},
                # },
            },
        },
        'sort': [
            '_score',
        ],
    })
    hits = results['hits']['hits']

    articles = [(h['_source'], h['_score']) for h in hits]

    return articles
