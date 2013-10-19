API = 'http://localhost:3000/api'



async.parallel [
	# (cb) ->
	# 	chrome.runtime.onConnect.addListener (port) ->
	# 		cb null, port
	(cb) ->
		$.getJSON API+'/words', (words) ->
			cb null, words
	(cb) ->
		$.getJSON API+'/user', (user) ->
			cb null, user
], (err, results) ->
	[allWords, user] = results
	words = {}
	words.common = "i you am a the he she it we they him her".split(' ')
	words.tracked = user.words
	words.untracked = _.difference allWords, words.tracked, words.common

	words.common.sort()
	words.tracked.sort()
	words.untracked.sort()

	chrome.runtime.onConnect.addListener (port) ->
		console.log 'listening...', port
		port.onMessage.addListener (msg) ->
			switch msg.action
				when 'update-word'
					console.log 'marking ' + msg
					lemma = msg.data.lemma
					$.post API + '/api/user/words', {
						action: 'update'
						lemma: lemma
					}
					, (data) ->
						port.postMessage
							id: 'update-word'
							data:
								lemma: lemma
								classification: 0
				else
					console.log 'got weird message' + msg
		
		port.postMessage
			id: 'load-words'
			data: words

