import itertools


def alpha_headings(words):
	def first_char(word):
		return word.lemma[:1].upper()
	groups = []
	for k, v in itertools.groupby(words, first_char):
		groups.append((k, list(v)))
	return groups