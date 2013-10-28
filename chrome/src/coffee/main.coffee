
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
# for messages from background script
port.onMessage.addListener (msg, sender) ->
	switch msg.id
		when 'load-words'
			bg.lemmata = msg.data.lemmata
			bg.lemmata.user = new LemmaPartition bg.lemmata.user
		when 'word-diff'
			diff = msg.data.diff
			kind = diff.addTo
			bg.lemmata.user.applyDiff diff
			for lemma in diff.lemmata
				superglot.updateKind lemma, kind
		when 'show-stats'
			if msg.data?.text?
				lemmata =  (_.uniq NLP.lemmatize NLP.segment msg.data.text).sort()
			else
				lemmata = superglot.getAllLemmata()
			stats = bg.lemmata.user.getIntersections lemmata
			console.log stats
		else
			console.warn 'got invalid message: ', msg

# for messages from browser action
chrome.runtime.onMessage.addListener (msg, sender, sendResponse) ->
	switch msg.id
		when 'stats-request'
			superglot.transform()
			sendResponse
				id: 'show-stats'
				data:
					stats: 
						totalWordCount: superglot.allLemmataRaw.length
						uniqueWords: superglot.getAllLemmata()
						intersections: bg.lemmata.user.getIntersections superglot.getAllLemmata()

			
class Superglot
	tokenSelector: 'span.sg'
	excludedTags: ['script', 'style', 'iframe', 'head', 'code', 'pre', 'textarea', 'input', 'svg', 'canvas']

	constructor: (@$root) ->
		@allLemmata = null
		@allLemmataRaw = []

	getAllLemmata: ->
		@allLemmata ?= (_.uniq @allLemmataRaw).sort()
		@allLemmata

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
		@$root.on 'mousemove', (e) =>
			@$root.removeClass 'is-adding-known is-adding-learning'
			if e.ctrlKey or e.metaKey
				@$root.addClass 'is-adding-known'
			else if e.altKey
				@$root.addClass 'is-adding-learning'
		@$root.find(@tokenSelector).on 'click', (e) =>
			$el = $(e.currentTarget)
			lemma = $el.data('lemma')
			kind = @classify lemma
			if kind in enums.STATIC_KINDS then return true
			else if not (e.ctrlKey or e.metaKey or e.altKey) then return true
			else
				e.preventDefault()
				inclusionKind = (
					if e.ctrlKey or e.metaKey then 'known' 
					else if e.altKey then 'learning'
					else null
				)
				diff = new LemmaDiff
					lemmata: [lemma]
					removeFrom: kind
					addTo: switch kind
						when 'common', 'ignored' then kind
						when inclusionKind then 'untracked'
						else inclusionKind
				if not diff.idempotent()
					port.postMessage
						id: 'word-diff'
						data:
							diff: diff
				else
					console.warn 'idempotent diff', diff
				return false
		

	transform: ->
		if not @$root.hasClass 'superglot'
			go = ($node) =>
				contents = $node.contents()
				onlyChild = contents.length == 1
				for c in contents
					if c.nodeType is 3 and c.length > 2  # nodeType 3 is TEXT
						words = NLP.segment c.data
						lemmata = words.map (w) => NLP.lemmatize w
						@allLemmataRaw = @allLemmataRaw.concat lemmata
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
