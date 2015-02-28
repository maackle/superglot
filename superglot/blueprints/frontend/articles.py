import re
from bs4 import BeautifulSoup
import requests

from flask import Blueprint, abort, render_template, request, flash, redirect, url_for, current_app as app
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _

from superglot.cache import cache
from superglot.forms import AddArticleForm
from superglot import models
from superglot import nlp
from superglot import util
from superglot.util import sorted_words
from superglot import formatting
from superglot.config import settings
from superglot import core
from pprint import pprint


blueprint = Blueprint('frontend.articles', __name__, template_folder='templates')


def article_stats(article):
    return core.user_article_stats(current_user, article)


@blueprint.route('/user/texts/', methods=['GET', 'POST'])
@login_required
def article_list():
    articles = models.Article.query().filter_by(user_id=current_user.id)
    articles_w_stats = [
        (article, article_stats(article)) for article in articles
    ]
    return render_template(
        'views/frontend/article_list.jade',
        articles_w_stats=articles_w_stats
    )


@blueprint.route('/user/texts/<article_id>/read', methods=['GET', 'POST'])
@login_required
def article_read(article_id):
    '''
    TODO: words with the same lemma are not marked as known
    '''
    article = app.db.session.query(models.Article).filter_by(
        user_id=current_user.id,
        id=article_id).first()
    if not article:
        abort(404)
    article_vocab_pairs = core.get_common_vocab_pairs(current_user, article)

    stats = core.vocab_stats([vo[0] for vo in article_vocab_pairs])

    # import pudb; pu.db
    # print(article_vocab_pairs)

    return render_template(
        'views/frontend/article_read.jade',
        article=article,
        stats=stats,
        article_vocab_pairs=article_vocab_pairs)


@blueprint.route('/texts/<article_id>/read', methods=['GET', 'POST'])
@login_required
def article_read_anon(article_id):
    '''
    TODO: words with the same lemma are not marked as known
    '''
    article = app.db.session.query(models.Article).filter_by(id=article_id).first()
    if not article:
        abort(404)
    article_vocab = core.get_common_vocab(current_user, article)
    stats = core.vocab_stats(article_vocab)

    return render_template(
        'views/frontend/article_read.jade',
        article=article,
        stats=stats,
        article_vocab=sorted(article_vocab))


@blueprint.route('/user/texts/<article_id>/delete/', methods=['GET', 'POST'])
@login_required
def article_delete(article_id):
    '''
    TODO: ensure the user owns the article!!
    '''
    article = app.db.session.query(models.Article).filter_by(id=article_id).first()
    t = models.Article.__table__
    deleted = app.db.engine.execute(t.delete().where(t.c.id == article_id))
    if deleted:
        flash(_('Deleted "%(title)s"', title=article.title))
    return redirect(url_for('.article_list'))


@blueprint.route('/user/texts/add/', methods=['GET', 'POST'])
@login_required
def article_create():

    def read_page(url):
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

    form = AddArticleForm()
    if form.validate_on_submit():
        url = form.url.data
        title = form.title.data
        plaintext = None

        if form.plaintext.data:
            plaintext = form.plaintext.data

        if url:
            (page_text, page_title) = read_page(url)
            if not plaintext:
                plaintext = page_text
            if not title:
                title = page_title

        if not title:
            if url:
                title = url
            else:
                title = '[untitled]'

        article, created = core.create_article(
            user=current_user,
            title=title,
            plaintext=plaintext,
            url=url,
        )

        # cache.delete_memoized(superglot.get_common_word_pairs, current_user, article)

        if created:
            flash("Added {}".format(title), 'success')
        else:
            flash("Updated {}".format(title), 'success')

        return redirect(url_for('frontend.articles.article_list'))
    else:
        return render_template('views/frontend/article_create.jade', form=form)

