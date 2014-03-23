from textblob import TextBlob, Word


def tokenize(text):
	blob = TextBlob(text)
	return blob.words

def lemmatize(text):
	return tokenize(text).lemmatize()

def lemmatize_word(word):
	return Word(word).lemmatize()

if __name__ == '__main__':
	sentence = """
	these octopi went to the best, tastiest restaurants
	"""
	lemmata = lemmatize(sentence)
	for l in lemmata:
		print(l)