
superglot = {}
bg = {
	words: {}
}

NLP = new nlp.NLP

wordCollection = (classification) ->
	switch classification
		when 'sg-known' then bg.words.known
		when 'sg-untracked' then bg.words.untracked
		when 'sg-common' then bg.words.common
		else throw "invalid classification: " + classification

port = chrome.runtime.connect()
port.onMessage.addListener (msg) ->
	switch msg.id
		when 'load-words'
			bg.words = msg.data
			console.log bg.words
			superglot.transform()
		when 'update-word'
			{lemma, classification} = msg.data
			superglot.updateClassification lemma, classification
			collection = wordCollection classification
			for loser in bg.words
				_.without loser, lemma
			collection.push lemma
			collection.sort()
		when 'show-stats'
			text = msg.text
			lemmata = _.uniq NLP.lemmatize NLP.segment text
			stats = 
				known: _.intersection lemmata, bg.words.known
				untracked: _.intersection lemmata, bg.words.untracked
				invalid: _.intersection lemmata, bg.words.invalid
			console.log stats
		else
			console.warn 'got invalid message: ', msg

			
class Superglot
	tokenSelector: 'span.sg'
	excludedTags: ['script', 'style', 'iframe', 'head', 'code']

	constructor: (@$root) ->

	updateClassification: (lemma, klass) ->
		@$root.find(".sg[data-lemma=#{lemma}]").each (i, el) =>
			$(el).removeClass 'sg-known sg-untracked'
			$(el).addClass klass

	toggleClassification: (wordEl) ->
		$el = $(wordEl)
		if $el.hasClass 'sg-untracked'
			$el.removeClass 'sg-untracked'
			$el.addClass 'sg-known'
		else
			$el.removeClass 'sg-known'
			$el.addClass 'sg-untracked'

	classify: (lemma) ->
		w = lemma
		if w in bg.words.common
			'sg-common'
		else if w in bg.words.known
			'sg-known'
		else if util.binarysearch(bg.words.untracked, w) >= 0
			'sg-untracked'
		else
			'sg-invalid'
 
	bindEvents: ->
		@$root.find(@tokenSelector).on 'click', (e) =>
			$el = $(e.currentTarget)
			lemma = $el.data('lemma')
			if $el.hasClass 'sg-untracked'
				port.postMessage
					action: 'add-word'
					data:
						lemma: lemma
			else if $el.hasClass 'sg-known'
				port.postMessage
					action: 'remove-word'
					data:
						lemma: lemma

	transform: ->
		go = ($node) =>
			contents = $node.contents()
			onlyChild = contents.length == 1
			for c in contents
				if c.nodeType is 3 and c.length > 2  # nodeType 3 is TEXT
					words = NLP.segment c.data
					tokens = words.map (w) => 
						lemma = NLP.lemmatize w
						klass = @classify lemma
						""" 
						<span data-lemma="#{lemma}" class="sg #{klass}">#{w}</span>
						"""
					html = tokens.join('')
					if onlyChild
						$node.html html
					else
						$(c).after(html).remove()
				else
					if c.nodeName.toLowerCase() not in @excludedTags
						go $(c)
		@$root.addClass 'superglot'
		go @$root
		@bindEvents()

$ ->
	console.debug 'superglot: DOM loaded'
	superglot = new Superglot $('body')
