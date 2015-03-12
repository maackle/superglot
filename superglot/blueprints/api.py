from collections import defaultdict

from flask import Blueprint, request, jsonify, current_app as app
from flask.ext.login import current_user, login_required

from superglot import models
from superglot import core


blueprint = Blueprint('api', __name__, template_folder='templates')


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


@blueprint.route('/words/translate/', methods=['GET',])
@login_required
def translate_word():
    word_id = request.args.get("word_id")

    word = app.db.session.query(models.Word).filter_by(id=word_id).first()
    meaning = word.lookup(current_user.native_language)

    return jsonify({
        'source_language': word.language,
        'source': word.reading,
        'target_language': meaning.language,
        'target': meaning.meaning,
    })