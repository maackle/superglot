markWords = (lemmata, group, after) ->
	lemmataString = lemmata.join("\n")
	$.post '/api/user/words/update/', {
		lemmata: lemmataString
		group: group
	}, after

addMeaningTooltip = (el, meaning) ->
	$(el).tooltip
		title: meaning
		placement: 'left'

$ ->
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

	$('.vocab-list li').mouseenter (e) ->
		el = this
		$el = $(el)
		wordId = $el.data('id')
		if $el.data('translation') is undefined
			$(el).data('translation', '')  # so we know we're working on it
			$.get '/api/words/translate/', { word_id: wordId }, (data) =>
				meaning = data.target
				addMeaningTooltip(el, meaning)
				$el.data('translation', meaning)
				$el.trigger 'mouseenter'