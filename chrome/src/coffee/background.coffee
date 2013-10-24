API = 'http://localhost:3000/api'

NLP = new nlp.NLP

chrome.contextMenus.create
	title: 'Get Stats'
	contexts: ['selection']
	onclick: (info, tab) ->
		text = info.selectionText
		tabPort[tab.id].postMessage
			id: 'show-stats'
			text: text

tabPort = {}

async.parallel [
	(cb) ->
		$.getJSON API+'/words', (words) ->
			console.log words
			cb null, words
	(cb) ->
		$.getJSON API+'/user', (user) ->
			cb null, user
], (err, results) ->
	[allWords, user] = results
	allLemmata = allWords.map (w) -> w.lemma
	words = {}
	words.common = "i you am a the he she it we they him her".split(' ')
	words.known = user.lemmata
	words.untracked = _.difference allLemmata, words.known, words.common

	words.common.sort()
	words.known.sort()
	words.untracked.sort()

	console.log words

	chrome.runtime.onConnect.addListener (port) ->
		console.log 'listening...', port
		if port.sender.tab?
			tabPort[port.sender.tab.id] = port
		port.onMessage.addListener (msg) ->
			switch msg.action
				when 'add-word', 'remove-word'
					[action, verb] = msg.action.match /(\w+)-word/
					lemma = msg.data.lemma
					$.ajax 
						url: API + "/user/words/#{verb}"
						type: 'post'
						dataType: 'json'
						data: {
							lemma: lemma
						}
						success: (data) ->
							port.postMessage
								id: 'update-word'
								data: data
				else
					console.warn 'got weird message', msg
		
		port.postMessage
			id: 'load-words'
			data: words

