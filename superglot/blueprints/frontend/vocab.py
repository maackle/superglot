
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app as app
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _

from superglot import models
from superglot import nlp
from superglot import core, util


blueprint = Blueprint('frontend.vocab', __name__, template_folder='templates')


@blueprint.route('/user/vocab/', methods=['GET', 'POST'])
@login_required
def word_list_all():
    return render_template('views/vocab/vocab_list.jade')


@blueprint.route('/user/vocab/<lemma>', methods=['GET'], endpoint='word')
@login_required
def vocab_word(lemma):
    W = models.Word
    A = models.Article
    VW = models.VocabWord
    WO = models.WordOccurrence
    occurrences = (
        app.db.session.query(WO)
        .join(W, A)
        .filter(A.user_id == current_user.id)  # TODO: allow public articles
        .filter(W.lemma == lemma)
    )
    vword = (
        VW.query
        .join(W)
        .filter(W.lemma == lemma)
        .filter(VW.user_id == WO.word_id)
        .first()
    )

    if not vword:
        raise util.InvalidUsage('Word not found')

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
