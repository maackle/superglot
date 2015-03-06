# WIP

annotateNode = ($node) =>
	contents = $node.contents()
	onlyChild = contents.length == 1
	for c in contents
		if c.nodeType is 3 and c.length > 2  # nodeType 3 is TEXT
			words = NLP.segment c.data
			lemmata = words.map (w) => NLP.lemmatize w
			@allLemmataRaw = @allLemmataRaw.concat lemmata
			console.debug 'tokens', tokens
			tokens = words.map (w) =>
				lemma = NLP.lemmatize w
				kind = @classify lemma
				"""
				<span data-lemma="#{lemma}" class="sg sg-#{kind}">#{w}</span>
				"""
			html = tokens.join('')
			if onlyChild
				$node.html html
			else
				$(c).after(html).remove()
		else
			if c.nodeName.toLowerCase() not in @excludedTags
				go $(c)

annotateDOM: ($root) ->
	if not @$root.hasClass 'superglot-annotated'

		@$root.addClass 'superglot-annotated'
		go @$root
		@bindEvents()
