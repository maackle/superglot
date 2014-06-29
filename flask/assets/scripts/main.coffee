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
		$.post '/api/user/words/update/', {
			lemma: lemma
			group: newGroup
		}, (data) ->
			if data
				$("[data-lemma='"+lemma+ "']").attr('data-group', newGroup)