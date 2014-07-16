from textblob import TextBlob, Word
import util

class Token:

	reading = None
	lemma = None

	def __init__(self, reading, lemma):
		self.reading = reading
		self.lemma = lemma

	def tup(self):
		return (self.reading, self.lemma)

	def __eq__(self, other):
		return self.reading == other.reading

	def __hash__(self):
		return util.string_hash(self.lemma + self.reading)


def get_sentences(text):
	return TextBlob(text).sentences

def tokenize(text):
	# TODO: keep track of occurence positions
	blob = TextBlob(text)
	sentences = blob.sentences
	tags = blob.tags
	words = blob.words

	def gen():
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

			yield Token(reading, Word(reading).lemmatize(pos).lower())

	return list(gen())


def lemmatize_word(word):
	return Word(word).lemmatize()

if __name__ == '__main__':
	sentence = """
	these octopi went to the best, tastiest restaurants
	"""
	lemmata = lemmatize(sentence)
	for l in lemmata:
		print(l)