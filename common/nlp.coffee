

class NLP

	segment: (text) ->
		text.split(/\s+|(?=[^a-zA-Z\s]+)/).filter (s) -> s

	lemmatize: (token) ->
		if typeof token == 'object'
			token.map @lemmatize
		else 
			token.toLowerCase().replace(" ", '')

window?.nlp = {}
(exports ? nlp).NLP = NLP