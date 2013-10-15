
words = {}
words.common = "i you am a the he she it we they him her".split(' ')
words.untracked = (Math.random().toString(32)[2...7] for a in [1..999999])
words.tracked = [
	'walrus'
]

words.common.sort()
words.tracked.sort()
words.untracked.sort()

chrome.runtime.onConnect.addListener (port) ->

	port.onMessage.addListener (msg) ->
		switch msg
			when 'debug-load'
				0

	port.postMessage
		id: 'load-words'
		data: words
