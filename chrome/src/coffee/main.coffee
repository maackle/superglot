TEXT_NODE_TYPE = 3

bg =
	words: {}

port = chrome.runtime.connect()
port.onMessage.addListener (msg) ->
	switch msg.id
		when 'load-words'
			bg.words = msg.data
			bg.words.tracked = window.corncobWords
			$ ->
				console.log 'DOM loaded'
				superglot = new Superglot $('body')
				superglot.transform()
		else
			console.log 'got message: ', msg



class Superglot
	tokenSelector: 'span.w'
	excludedTags: ['script', 'style', 'iframe', 'head']

	constructor: (@$root) ->

	tokenize: (text) ->
		text.split(/\s+|(?=[^a-zA-Z\s]+)/).filter (s) -> s

	classify: (word) ->
		w = word.toLowerCase()
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
			port.postMessage
				action: 'mark'
				word: $(e.currentTarget).text()

	transform: ->
		go = ($node) =>
			contents = $node.contents()
			onlyChild = contents.length == 1
			for c in contents
				if c.nodeType is TEXT_NODE_TYPE and c.length > 2
					words = @tokenize c.data
					tokens = words.map (w) => 
						klass = @classify w
						""" 
						<span class="sg #{klass}">#{w}</span>
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

