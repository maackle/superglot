$ ->

	markWords = (lemmata, group, after) ->
		lemmataString = lemmata.join("\n")
		$.post '/api/user/words/update/', {
			lemmata: lemmataString
			group: group
		}, after


	$('.annotated-word-list li').click (e) ->
		$el = $(this)
		if $el.attr('data-group') == 'ignored'
			return false
		lemma = $el.data('lemma')
		group = $el.attr('data-group')
		if group == 'known'
			newGroup = 'learning'
		else
			newGroup = 'known'

		markWords [lemma], newGroup, (data) ->
			if data
				$("[data-lemma='"+lemma+ "']").attr('data-group', newGroup)

	$('.annotated-word-list .controls .mark-all').click (e) ->
		group = $(this).attr('data-group')
		$affected = $('.annotated-word-list li')
			.filter (i, el) ->
				$(el).attr('data-group') != group
		lemmata = $affected
			.map (i, el) ->
				$(el).attr('data-lemma')
			.get()
		markWords lemmata, group, (data) ->
			$affected.attr('data-group', group)