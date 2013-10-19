TEXT_NODE_TYPE = 3

bg =
	words: {}

port = chrome.runtime.connect()
port.onMessage.addListener (msg) ->
	switch msg.id
		when 'load-words'
			bg.words = msg.data
			$ ->
				console.debug 'DOM loaded'
				superglot = new Superglot $('body')
				superglot.transform()
		else
			console.debug 'got message: ', msg



class Superglot
	tokenSelector: 'span.sg'
	excludedTags: ['script', 'style', 'iframe', 'head', 'code']

	constructor: (@$root) ->

	tokenize: (text) ->
		text.split(/\s+|(?=[^a-zA-Z\s]+)/).filter (s) -> s

	lemmatize: (word) ->
		word.toLowerCase().replace(" ", '')

	toggleClassification: (wordEl) ->
		$el = $(wordEl)
		if $el.hasClass 'sg-untracked'
			$el.removeClass 'sg-untracked'
			$el.addClass 'sg-tracked'
		else
			$el.removeClass 'sg-tracked'
			$el.addClass 'sg-untracked'

	classify: (lemma) ->
		w = lemma
		if w in bg.words.common
			'sg-common'
		else if w in bg.words.tracked
			'sg-tracked'
		else if bg.words.untracked.binarysearch(w) >= 0
			'sg-untracked'
		else
			'sg-unknown'
 
	bindEvents: ->
		@$root.find(@tokenSelector).on 'click', (e) =>
			$el = $(e.currentTarget)
			lemma = $el.data('lemma')
			@$root.find(".sg[data-lemma=#{lemma}]").each (i, el) =>
				@toggleClassification el
			port.postMessage
				action: 'update-word'
				data:
					lemma: lemma

	transform: ->
		go = ($node) =>
			contents = $node.contents()
			onlyChild = contents.length == 1
			for c in contents
				if c.nodeType is TEXT_NODE_TYPE and c.length > 2
					words = @tokenize c.data
					tokens = words.map (w) => 
						lemma = @lemmatize w
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

