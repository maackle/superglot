API = API_URL

xhrUser = $.ajax
	url: API + '/user'
	type: 'get'
	dataType: 'json'

xhrUser.done (user) ->
	if user?
		chrome.tabs.query  # get the active tab
			active: true
			currentWindow: true
		, (tabs) ->
			[tab] = tabs  # (there will be only one...unless there are multiple windows?)
			chrome.tabs.sendMessage tab.id,
				id: 'stats-request'
			, (response) ->
				console.log response
				mkPercent = (r) ->
					p = 100 * r
					if p < 10 then p.toFixed(1) else parseInt(p)
				stats = response.data.stats
				totalCount = stats.totalWordCount
				uniqueCount = stats.uniqueWords.length
				{known, learning, ignored} = stats.intersections
				$ ->
					$('.percent-known').text mkPercent known.length / uniqueCount
					$('.percent-learning').text mkPercent learning.length / uniqueCount

					$('.total-all').text totalCount
					$('.total-unique').text uniqueCount
					$('.total-known').text known.length
					$('.total-learning').text learning.length
					$('.total-ignored').text ignored.length

					$('.case.logged-in').show()
	else
		$ ->
			$('.case.logged-out').show().find('form').on 'submit', (e) ->
				console.log 'submit'
				xhrLogin = $.ajax
					url: SITE_URL + '/login'
					type: 'post'
					data:
						username: $(this).find('[name=username]').val()

				xhrLogin.done (res) ->
					console.log 'login: ', res
				xhrLogin.fail ->
					console.log 'failure', arguments


xhrUser.fail (err) ->
	console.error 'error:', arguments
	$('.case.error').show()


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