$ ->
	$('a').click (e) ->
		console.log 'haaallloo'

chrome.tabs.query
	active: true
	currentWindow: true
, (tabs) ->
	[tab] = tabs
	chrome.tabs.sendMessage tab.id,
		id: 'stats-request'
	, (response) ->
		mkPercent = (r) ->
			p = 100 * r
			if p < 10 then p.toFixed(1) else parseInt(p)
		stats = response.data.stats
		totalCount = stats.totalWordCount
		uniqueCount = stats.uniqueWords.length
		{known, learning, ignored} = stats.intersections

		$('.percent-known').text mkPercent known.length / uniqueCount
		$('.percent-learning').text mkPercent learning.length / uniqueCount
		
		$('.total-all').text totalCount
		$('.total-unique').text uniqueCount
		$('.total-known').text known.length
		$('.total-learning').text learning.length
		$('.total-ignored').text ignored.length


# tabPorts = {}

# console.debug 'opened...', tabPorts

# chrome.runtime.onConnect.addListener (port) ->
# 	console.log 'listening...', port
# 	if port.sender.tab?
# 		tabPorts[port.sender.tab.id] = port
# 	port.postMessage
# 		id: 'stats-request'
# 	, (res) ->
# 		console.log 'response: ', res