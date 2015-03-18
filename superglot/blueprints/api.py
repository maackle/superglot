from collections import defaultdict

from flask import Blueprint, request, jsonify, current_app as app
from flask.ext.login import current_user, login_required
from flask.ext.restful import reqparse

from superglot import core, models, nlp, util


blueprint = Blueprint('api', __name__, template_folder='templates')


def make_response(data, error_msg=None):
    if error_msg:
        data.update({
            'status': 'error',
            'message': error_msg
        })
    else:
        data.update({'status': 'success'})
    return jsonify(data)


@blueprint.route('/')
def index():
    return 'API v1.0'


@blueprint.route('/user/vocab/due', methods=['GET'])
@login_required
def due_vocab():
    vocab = core.gen_due_vocab(current_user)
    vocab_json = [v.to_json() for v in vocab]
    counts = defaultdict(int)
    for v in vocab:
        counts[v.rating] += 1

    return jsonify({
        'total': len(vocab),
        'due_vocab': vocab_json,
        'counts': counts,
    })


def nullint(v):
    return int(v or 0)


def nonestr(v):
    return str(v) or None


@blueprint.route('/user/vocab/', methods=['GET'])
@login_required
def vocab_search():
    parser = reqparse.RequestParser()
    parser.add_argument('prefix', type=str)
    parser.add_argument('size', type=int)
    parser.add_argument('page', type=int)
    parser.add_argument('rating', type=nonestr)  # None or 1,2,3
    args = parser.parse_args()
    ratings = args['rating'].split(',')

    start = args['page'] * args['size']
    end = start + args['size']

    vocab = core.user_vocab_search(
        user=current_user,
        prefix=args['prefix'],
        ratings=ratings,
    )

    total = vocab.count()

    vocab = vocab[start:end]
    vocab_json = [v.to_json() for v in vocab]
    return make_response({
        'vocab': vocab_json,
        'total': total,
    })


@blueprint.route('/user/words/update/', methods=['POST',])
@login_required
def update_word():
    lemmata = request.form.get('lemmata').split('\n')
    rating = request.form.get('rating')
    rating = int(rating)

    changes = []

    for lemma in lemmata:
        word = app.db.session.query(models.Word).filter_by(lemma=lemma).first()
        change = core.update_user_words(current_user, [word], rating)

        if change:
            changes.append({
                'lemma': lemma,
                'rating': rating,
            })
        else:
            changes.append('false')

    return jsonify({'changes': changes})


@blueprint.route('/words/translate/', methods=['POST'])
@login_required
def translate_words():
    word_ids = request.form.getlist("word_ids[]")
    lemmata = []
    meanings = {}
    native_language = current_user.native_language
    for word_id in word_ids:
        word = models.Word.query.filter_by(id=word_id).first()
        if not word:
            raise util.InvalidUsage('Word not found: %s' % word_id)

        translation = models.WordTranslation.query.filter_by(
            word_id=word_id,
            language=current_user.native_language
        ).first()

        if not translation:
            try:
                meaning = nlp.translate_word(
                    word.lemma, current_user.native_language)
            except:
                meaning = None
            translation = models.WordTranslation(
                word_id=word_id,
                language=native_language,
                meaning=meaning,
            )
            app.db.session.add(translation)
            app.db.session.commit()

        lemmata.append(word.lemma)
        meanings[word.lemma] = translation.meaning

    return jsonify({
        'target_language': native_language,
        'lemmata': lemmata,
        'meanings': meanings,
    })
