
superglot = {}
bg = {
	lemmata: {}
}

NLP = new nlp.NLP

wordCollection = (classification) ->
	switch classification
		when 'sg-known' then bg.lemmata.known
		when 'sg-learning' then bg.lemmata.learning
		when 'sg-ignored' then bg.lemmata.ignored
		when 'sg-common' then bg.lemmata.common
		else throw "invalid classification: " + classification

port = chrome.runtime.connect()
port.onMessage.addListener (msg) ->
	switch msg.id
		when 'load-words'
			bg.lemmata = msg.data.lemmata
			bg.lemmata.user = new LemmaPartition bg.lemmata.user
			superglot.transform()
		when 'word-diff'
			diff = msg.data.diff
			kind = diff.addTo
			bg.lemmata.user.applyDiff diff
			for lemma in diff.lemmata
				superglot.updateKind lemma, kind
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
	excludedTags: ['script', 'style', 'iframe', 'head', 'code', 'pre', 'textarea', 'input', 'svg', 'canvas']

	constructor: (@$root) ->

	updateKind: (lemma, kind) ->
		@$root.find(".sg[data-lemma=#{lemma}]").each (i, el) =>
			$(el).removeClass ('sg-'+k for k in enums.KINDS).join(' ')
			$(el).addClass ('sg-'+kind) if kind

	classify: (lemma) ->
		w = lemma
		if w in bg.lemmata.common then 'common'
		else if w in bg.lemmata.user.ignored then 'ignored'
		else if w in bg.lemmata.user.known then 'known'
		else if w in bg.lemmata.user.learning then 'learning'
		else if util.binarysearch(bg.lemmata.all, w) >= 0 then 'untracked'
		else 'invalid'
 
	bindEvents: ->
		@$root.find(@tokenSelector).on 'click', (e) =>
			$el = $(e.currentTarget)
			lemma = $el.data('lemma')
			kind = @classify lemma
			if kind in enums.STATIC_KINDS then return
			else
				inclusionKind = if e.ctrlKey then 'known' else 'learning'
				diff = new LemmaDiff
					lemmata: [lemma]
					removeFrom: kind
					addTo: switch kind
						when 'common', 'ignored' then kind
						when inclusionKind then 'untracked'
						else inclusionKind
				if not diff.idempotent()
					port.postMessage
						action: 'word-diff'
						data:
							diff: diff
				else
					console.warn 'idempotent diff', diff
		

	transform: ->
		go = ($node) =>
			contents = $node.contents()
			onlyChild = contents.length == 1
			for c in contents
				if c.nodeType is 3 and c.length > 2  # nodeType 3 is TEXT
					words = NLP.segment c.data
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
		@$root.addClass 'superglot'
		go @$root
		@bindEvents()

$ ->
	console.debug 'superglot: DOM loaded'
	superglot = new Superglot $('body')
