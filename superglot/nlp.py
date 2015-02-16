import textblob
from superglot import util
import nltk
from nltk.tokenize import PunktWordTokenizer


pw_tokenizer = PunktWordTokenizer()


class Token:

    reading = None
    lemma = None
    pos = None

    def __init__(self, reading, lemma, pos):
        self.reading = reading
        self.lemma = lemma
        self.pos = pos

    def tup(self):
        return (self.reading, self.lemma)

    def __eq__(self, other):
        return self.reading == other.reading

    def __hash__(self):
        return util.string_hash(self.lemma + self.reading)


def translate_word(text, language):
    blob = textblob.TextBlob(text)
    return str(blob.translate(to=language))


def get_sentences(text):
    return textblob.TextBlob(text).sentences


def tokenize(text):
    # TODO: keep track of occurence positions
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
            lemma=textblob.Word(reading).lemmatize(pos).lower(),
            pos=pos,
        )
        toks.append(token)

    return toks


def tokenize2(text):
    return pw_tokenizer.tokenize(text)


def span_tokenize(text):
    return pw_tokenizer.span_tokenize(text)


def tokenize_with_spans(text):
    tokens = pw_tokenizer.tokenize(text)
    spans = pw_tokenizer.span_tokenize(text)
    return zip(tokens, spans)


def get_reading_lemmata(reading):
    '''
    Get all possible lemmata for a reading
    '''
    reading = reading.lower()
    return [textblob.Word(reading).lemmatize(pos).lower() for pos in "nva"]

