markWords = (lemmata, label, after) ->
	lemmataString = lemmata.join("\n")
	$.post '/api/user/words/update/', {
		lemmata: lemmataString
		label: label
	}, after

addMeaningTooltip = (el, meaning) ->
	$(el).tooltip
		title: meaning
		placement: 'left'

setupAnnotation = ->

	selectWord = (el) ->
		$word = $(el)
		if not $word.hasClass('selected')
			deselectWords()
			$word.addClass('selected')
			showWordScorePopup(el)
		else
			deselectWords()

	deselectWords = ->
		$('.annotated-words li').removeClass('selected')
		hideWordScorePopup()

	updateWord = (el, score) ->
		lemma = $(el).attr('data-lemma')
		if score < 3
			label = 'learning'
		else
			label = 'known'
		markWords [lemma], label, (data) ->
			if data
				$("[data-lemma='"+lemma+ "']").attr('data-group-label', label)
				deselectWords()

	showWordScorePopup = (el) ->
		# TODO: link score to word, must switch over from labels... 
		$popup = $('#word-score-popup')
		$popup.show().focus()
		$(document).on 'keypress', (e) ->
			char = String.fromCharCode(e.keyCode)
			score = parseInt(char, 10)
			if score >= 0 and score <= 5
				$popup.find("input[value=\"#{ score }\"]").prop('checked', 1)
				updateWord(el, score)

	hideWordScorePopup = (el) ->
		$popup = $('#word-score-popup')
		$popup.hide()
		$(document).off 'keypress'

	attachAnnotationControls = ($el) ->
		$popup = $('#word-score-popup')
		$el.click (e) ->
			selectWord(this)

	attachAnnotationControls( $('.annotated-word-list li') )


$ ->
	setupAnnotation()
		

	# $('.annotated-word-list li').click (e) ->
	# 		$el = $(this)
	# 		if $el.attr('data-group-label') == 'ignored'
	# 			return false
	# 		lemma = $el.data('lemma')
	# 		label = $el.attr('data-group-label')
	# 		if label == 'known'
	# 			newGroup = 'learning'
	# 		else
	# 			newGroup = 'known'

	# 		markWords [lemma], newGroup, (data) ->
	# 			if data
	# 				$("[data-lemma='"+lemma+ "']").attr('data-group-label', newGroup)

	$('.annotated-word-list .controls .mark-all').click (e) ->
		label = $(this).attr('data-group-label')
		$affected = $('.annotated-word-list li')
			.filter (i, el) ->
				$(el).attr('data-group-label') != label
		lemmata = $affected
			.map (i, el) ->
				$(el).attr('data-lemma')
			.get()
		markWords lemmata, label, (data) ->
			$affected.attr('data-group-label', label)

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

	$('.accordion').accordion({
		header: '.header',
		collapsible: true,
	});