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

userLemmata = {}

console.log 'ready to load data'

async.parallel [
	(cb) ->
		if localStorage['superglot-lemmata']?
			lemmata = $.parseJSON localStorage['superglot-lemmata']
			console.debug 'loaded lemmata from localStorage'
			cb null, lemmata
		else
			$.getJSON API + '/words/lemmata', (lemmata) ->
				localStorage['superglot-lemmata'] = JSON.stringify lemmata
				cb null, lemmata
	(cb) ->
		$.getJSON API + '/user', (user) ->
			cb null, user

], (err, results) ->
	[lemmata, user] = results

	userLemmata = new LemmaPartition
		known: user.lemmata.known
		learning: user.lemmata.learning
		ignored: user.lemmata.ignored

	chrome.runtime.onConnect.addListener (port) ->
		console.log 'listening...', port
		if port.sender.tab?
			tabPort[port.sender.tab.id] = port
		port.onMessage.addListener (msg) ->
			switch msg.action
				when 'word-diff'
					diff = msg.data.diff
					# TODO: apply diff earlier, reverse on failure
					$.ajax 
						url: API + "/user/words/apply-diffs"
						type: 'post'
						dataType: 'json'
						data:
							diffs: JSON.stringify [diff]
						
						success: (data) ->
							console.log 'applying diff', diff
							console.log userLemmata
							userLemmata.applyDiff diff
							console.log userLemmata
							port.postMessage
								id: 'word-diff'
								data: 
									diff: diff
				else
					console.warn 'got weird message', msg
		
		port.postMessage
			id: 'load-words'
			data: 
				lemmata:
					all: lemmata.all
					common: lemmata.common
					user: userLemmata

