from collections import defaultdict

from flask import Blueprint, request, jsonify, current_app as app
from flask.ext.login import current_user, login_required

from superglot import core, models, nlp, util


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


@blueprint.route('/words/translate/', methods=['POST'])
@login_required
def translate_word():
    word_ids = request.form.getlist("word_ids[]")
    lemmata = []
    meanings = {}
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
                language=current_user.native_language,
                meaning=meaning,
            )
            app.db.session.add(translation)
            app.db.session.commit()

        lemmata.append(word.lemma)
        meanings[word.lemma] = translation.meaning

    return jsonify({
        'source_language': word.language,
        'target_language': translation.language,
        'lemmata': lemmata,
        'meanings': meanings,
    })
