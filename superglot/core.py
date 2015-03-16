'''
Complex queries, calculations, etc.
'''

import datetime
import re
from collections import defaultdict

from bs4 import BeautifulSoup

from flask import current_app as app
from flask.ext import security

from superglot.config import settings
from superglot import (
    nlp,
    util,
    models,
    database,
    srs,
)


def add_word(session, reading, lemma, language='en'):
    word = models.Word(lemma=lemma, language=language, canonical=False)
    session.add(word)
    session.add(models.LemmaReading(lemma=lemma, reading=reading))
    return word


def fetch_remote_article(url):
    ignored_tags = ['script', 'style', 'head', 'code', 'iframe']
    req = util.get_url(url)
    soup = BeautifulSoup(req.text)
    title = soup.title.text
    # remove noisy content-empty tags
    for tag in ignored_tags:
        for t in soup(tag):
            t.decompose()

    strings = (soup.stripped_strings)
    strings = (map(lambda x: re.sub(r"\s+", ' ', x), strings))
    plaintext = "\n".join(strings)
    return (plaintext, title)


def gen_due_vocab(user):
    '''
    Get VocabWords that are due for study for this user

    TODO: use actual query for filtering
    '''

    vwords = (
        item for item in user.vocab.all()
        if item.rating >= srs.RATING_MIN
        and item.srs_next_repetition
        and item.srs_next_repetition < util.now()
    )
    return sorted(vwords, key=lambda v: v.srs_next_repetition)


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

    return (
        _get_common_vocab_pairs_query(user, article)
        .order_by(models.WordOccurrence.article_position)
        .all()
    )


# @cache.memoize()
def get_common_word_ids(user, article):
    '''
    Get Words in the article
    '''

    V = models.VocabWord
    return (v[0] for v in _get_common_vocab_query(user, article).values(V.word_id))


def user_vocab_search(user, prefix, rating=None):
    vocab = user.vocab.join(models.Word).order_by(models.Word.lemma)
    if prefix:
        vocab = vocab.filter(models.Word.lemma.ilike(prefix + '%'))
    if rating:
        vocab = vocab.filter(models.VocabWord.rating == rating)
    return vocab


def _gen_words_from_readings(readings):
    '''
    DEPRECATED

    Look up words from token objects. If not in database, create a "non-canonical" word
    '''
    lemma_readings = defaultdict(set)
    reading_lemmata = defaultdict(set)
    reading_words = defaultdict(set)

    for reading in readings:
        for lemma in nlp.get_reading_lemmata(reading):
            lemma_readings[lemma].add(reading)
            reading_lemmata[reading].add(lemma)
            app.db.session.add(models.LemmaReading(lemma=lemma, reading=reading))
    app.db.session.commit()

    word_hash = {}
    words = []

    for chunk in util.chunked(lemma_readings.items(), 500):
        new_words = []
        for lemma, readings in chunk:
            word = (
                word_hash.get(lemma) or
                app.db.session.query(models.Word).filter_by(
                    lemma=lemma,
                    language='en'
                ).first()
            )
            if not word:
                word = models.Word(
                    lemma=lemma,
                    language='en',
                    canonical=False
                )
                new_words.append(word)
            words.append(word)
            word_hash[word.lemma] = word
            for reading in readings:
                reading_words[reading].add(word)

        app.db.session.add_all(new_words)
        app.db.session.commit()

    return reading_words


def gen_words_from_tokens(tokens):
    '''
    Look up words from token objects. If not in database, create a "non-canonical" word
    '''
    W = models.Word
    word_hash = {}
    words = []
    for chunk in util.chunked(tokens, 500):
        new_words = []
        lemmata = [tok.lemma for tok in chunk]
        known_words = W.query.filter(W.lemma.in_(lemmata)).all()
        word_hash = {word.lemma: word for word in known_words}
        for token in chunk:
            # try to get a word from the word_hash, fallback to database
            word = word_hash.get(token.lemma)
            if not word:
                word = models.Word(
                    lemma=token.lemma,
                    language='en',
                    canonical=False
                )
                new_words.append(word)
                word_hash[word.lemma] = word
            words.append(word)

        app.db.session.add_all(new_words)
        app.db.session.commit()

    return words


def create_article(user, title, plaintext, url=None):
    '''
    TODO: save sentence info?
    '''

    sentence_positions = {}
    occurrences = []

    tokens = nlp.tokenize(plaintext)
    spans = nlp.span_tokenize(plaintext)
    words = gen_words_from_tokens(tokens)

    for word, token, span in zip(words, tokens, spans):
        occ = models.WordOccurrence(
            word_id=word.id,
            reading=token.reading,
            article_position=span[0],
            # article_sentence_start=sentence.start
        )
        occurrences.append(occ)

    # for i, sentence in enumerate(sentences):
    #     sentence_positions[sentence.start] = len(sentence)
    #     sentence_tokens = nlp.tokenize(sentence.string)
    #     spans = nlp.span_tokenize(sentence.string)
    #     for reading, span in zip(readings, spans):
    #         words = reading_words[reading]
    #         for word in words:  # TODO: select only ONE word...
    #             if word.id:
    #                 occurrence = models.WordOccurrence(
    #                     word_id=word.id,
    #                     reading=reading,
    #                     article_position=(sentence.start + span[0]),
    #                     article_sentence_start=sentence.start
    #                 )
    #                 occurrences.append(occurrence)

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
        app.db.session.add(o)
    app.db.session.commit()

    # existing_vocab_word_ids = set(get_common_word_ids(user, article))
    # all_word_ids = {word.id for word in words}

    # TODO: merge?
    # for word_id in all_word_ids - existing_vocab_word_ids:
    for word in words:
        app.db.session.merge(
            models.VocabWord(user_id=user.id, word_id=word.id, rating=0)
        )
    app.db.session.commit()

    # cache.delete_memoized(get_common_word_pairs, user=user, article=article)

    return article, True


def _create_article_from_def(user, article_def):
    with open(article_def['file'], 'r') as f:
        plaintext = f.read()
        with util.Timer() as t:
            article, created = create_article(
                user=user,
                title=article_def['title'],
                plaintext=plaintext[0:]
            )
        print("created '{}' (length: {}) in {} ms".format(
            article.title,
            len(article.plaintext),
            t.msecs
        ))
    return article


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
    user = app.db.session.query(models.User).filter_by(email=email).first()
    if user and security.utils.verify_password(password, user.password):
        return user
    else:
        return None


def register_user(email, password):
    session = app.db.session
    user = session.query(models.User).filter_by(email=email).first()
    if user:
        created = False
    else:
        pw_hash = security.utils.encrypt_password(password)
        user = models.user_datastore.create_user(email=email, password=pw_hash)
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
    return updated_vocab


#############################################################

def get_article_sentences(article, words):
    '''Get all sentences that contain these words'''

    indices = """
    SELECT sentence_start from word_occurrence
    WHERE word_id IN ({word_ids}) AND article_id = {article.id}
    """

    O = models.WordOccurrence
    word_ids = list(w.id for w in words)
    sentence_starts = set(map(lambda r: r[0], (O.query
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
    stats = vocab_stats(vocab)
    return stats
    # groups = util.multi_dict_from_seq(vocab, lambda v: v.rating)


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
