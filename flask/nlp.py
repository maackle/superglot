from textblob import TextBlob, Word

def tokenize(text):
	# TODO: keep track of occurence positions
	blob = TextBlob(text)
	tags = blob.tags
	words = blob.words

	def gen():
		for reading, pos_abbr in tags:
			keep_case = False
			# if pos_abbr.startswith('NNP'):  # proper noun
			# 	pos = 'n'
			if pos_abbr.startswith('N'):  # noun
				keep_case = True
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

			yield (reading, Word(reading).lemmatize(pos).lower())

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