
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app as app
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _

from superglot import models
from superglot import nlp
from superglot.config import settings
from superglot import core, util


blueprint = Blueprint('frontend.vocab', __name__, template_folder='templates')


@blueprint.route('/user/vocab/', methods=['GET', 'POST'])
@login_required
def word_list_all():
    return render_template('views/vocab/vocab_list.jade')


@blueprint.route('/user/vocab/<lemma>', methods=['GET'], endpoint='word')
@login_required
def vocab_word(lemma):
    VW = models.VocabWord
    W = models.Word
    WO = models.WordOccurrence
    pairs = (
        app.db.session.query(VW, WO)
        .join(W)
        .filter(VW.user_id == current_user.id)
        .filter(W.lemma == lemma)
        .filter(VW.word_id == WO.word_id)
    )
    one = pairs.first()
    if not one:
        raise util.InvalidUsage('Word not found')
    vword = one[0]
    occurrences = (p[1] for p in pairs)
    return render_template(
        'views/vocab/vocab_word.jade',
        vword=vword,
        occurrences=occurrences,
    )


@blueprint.route('/user/vocab/delete/', methods=['GET', 'POST'])
@login_required
def delete_all_words():
    current_user.delete_all_words()
    flash(_('Deleted all words!'))
    return redirect(url_for('frontend.vocab.word_list_all'))


@blueprint.route('/user/vocab/<partition>/', methods=['GET', 'POST'])
@login_required
def word_list(partition):
    vocab = current_user.vocab_lists()
    words = vocab[partition]
    words.sort(key=models.Word.sort_key)
    return render_template('views/frontend/word_list.jade', words=words)


@blueprint.route('/user/vocab/add/<rating>/', methods=['POST'])
@login_required
def add_words(rating):
    if not (-1 <= rating and rating <= 3):
        raise "Invalid rating"
    tokens = nlp.tokenize(request.form['words'])
    new_words = core.gen_words_from_tokens(tokens)
    updated, ignored = core.update_user_words(current_user, new_words, rating, force=True)
    if updated == 0:
        flash('None of those words were recognized :(')
    else:
        flash('updated {}, ignored {}'.format(updated, ignored))
    return redirect(url_for('frontend.vocab.word_list_all'))
