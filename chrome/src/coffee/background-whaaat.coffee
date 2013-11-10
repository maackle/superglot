API = API_URL

NLP = new nlp.NLP

chrome.contextMenus.create
	title: "Get Stats for '%s'"
	contexts: ['selection']
	onclick: (info, tab) ->
		text = info.selectionText
		tabPorts[tab.id].postMessage
			id: 'show-stats'
			data:
				text: text

chrome.contextMenus.create
	title: 'Get Stats'
	contexts: ['page']
	onclick: (info, tab) ->
		tabPorts[tab.id].postMessage
			id: 'show-stats'


tabPorts = {}

userLemmata = {}

console.debug 'ready to load data'

async.parallel [
	(cb) ->
		chrome.storage.local.get 'superglot-lemmata', (storage) ->
			if storage['superglot-lemmata']?
				cb null, storage['superglot-lemmata']
				console.debug 'loaded lemmata from chrome.storage.local'
			else
				console.debug 'downloading from server...'
				$.getJSON API + '/words/lemmata', (lemmata) ->
					console.debug 'downloaded lemmata from server'
					chrome.storage.local.set 'superglot-lemmata': lemmata, ->
						console.debug 'saved to storage: ', arguments, chrome.runtime.lastError
						cb null, lemmata
	(cb) ->
		$.getJSON API + "/user", (user) ->
			cb null, user
		# TODO: make this only happen after successful login from the popup

		# chrome.cookies.get
		# 	url: 'http://superglot.com'
		# 	name: 'connect.sid'
		# , (cookie) ->
		# 	if cookie
		# 		sid = cookie.value
		# 		$.getJSON API + "/user", (user) ->
		# 			cb null, user
		# 	else
		# 		cb "no session cookie", null

], (err, results) ->
	if err
		console.error err
		return
	console.debug 'words and user loaded'
	[lemmata, user] = results

	userLemmata = new LemmaPartition
		known: user.lemmata.known
		learning: user.lemmata.learning
		ignored: user.lemmata.ignored

	chrome.runtime.onConnect.addListener (port) ->
		console.log 'listening...', port
		if port.sender.tab?
			tabPorts[port.sender.tab.id] = port

		port.onMessage.addListener (msg) ->
			switch msg.id
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

