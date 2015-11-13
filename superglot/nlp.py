import re

import nltk
from nltk.tokenize import PunktWordTokenizer
import textblob

from superglot import util


pw_tokenizer = PunktWordTokenizer()


def lemmatize(reading, pos):
    return textblob.Word(reading).lemmatize(pos).lower()


class Token:
    ''' Lightweight wrapper around a reading and a part of speech
    '''
    reading = None
    pos = None
    _lemma = None

    def __init__(self, reading, pos, lemma=None):
        self.reading = reading
        self.pos = pos
        self._lemma = lemma

    def tup(self):
        ''' Deprecated '''
        return (self.reading, self.lemma)

    @property
    def lemma(self):
        if not self._lemma:
            # self._lemma = lemmatize(self.reading, self.pos)
            raise Exception("lazy lemma now unsupported")
        return self._lemma

    @property
    def is_punctuation(token):
        return (
            not token.pos
            or token.pos in (':', '.', ',', '-NONE-')
            or token.reading in ('"',)
        )

    def __eq__(self, other):
        return self.reading == other.reading

    def __hash__(self):
        return util.string_hash(self.lemma + self.reading)

    def __str__(self):
        return "%s|%s (%s)" % (self.reading, self.pos, self.lemma)


def translate_word(text, source_language, target_language):
    print("TRW", text, source_language, target_language)
    blob = textblob.TextBlob(text)
    return str(blob.translate(from_lang=source_language, to=target_language))


def get_sentences(text):
    return textblob.TextBlob(text).sentences


_re_hyphen = re.compile(r'(\S+)—(\S+)')


def _pre_tokenize(text, language):
    ''' Fix it up a little
    '''
    text = _re_hyphen.sub(r'\1 — \2', text)
    return text


def tokenize(text, language):
    # TODO: keep track of occurence positions
    text = _pre_tokenize(text, language)
    words = pw_tokenizer.tokenize(text)
    tags = nltk.pos_tag(words)

    toks = []
    for reading, pos_abbr in tags:
        keep_case = False
        if pos_abbr.startswith('NNP'):  # proper noun
            keep_case = True
            pos = 'n'
        if pos_abbr.startswith('N'):  # noun
            pos = 'n'
        elif pos_abbr.startswith('V'):  # verb
            pos = 'v'
        elif pos_abbr.startswith('J'):  # adjective
            pos = 'a'
        else:
            pos = None

        is_acronym = reading.upper() is reading

        if not keep_case and not is_acronym:
            reading = reading.lower()

        token = Token(
            reading=reading,
            pos=pos,
            lemma=lemmatize(reading, pos)
        )
        toks.append(token)

    return toks


def span_tokenize(text, language):
    return pw_tokenizer.span_tokenize(text)


def tokenize_with_spans(text, language):
    tokens = pw_tokenizer.tokenize(text)
    spans = pw_tokenizer.span_tokenize(text)
    return zip(tokens, spans)


def get_reading_lemmata(reading):
    '''
    Get all possible lemmata for a reading
    '''
    reading = reading.lower()
    return [textblob.Word(reading).lemmatize(pos).lower() for pos in "nva"]
