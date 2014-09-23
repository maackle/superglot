SRS_SCORE_CHOICES = [1,2,3,4]

markWords = (lemmata, score, after) ->
	if score == 'known'
		score = 4
	else if score == 'learning'
		score = 2

	score = parseInt(score, 10)

	lemmataString = lemmata.join("\n")
	$.post '/api/user/words/update/', {
		lemmata: lemmataString
		score: score
	}, after

addMeaningTooltip = (el, meaning) ->
	$(el).tooltip
		title: meaning
		placement: 'left'

setupAnnotation = ->
	$popup = $('#word-score-popup')
	$popupChoices = $popup.find('.scores .choice')

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
		if score <= 0
			label = null
		else if score < 3
			label = 'learning'
		else
			label = 'known'
		markWords [lemma], score, (data) ->
			if data
				$(el).attr('data-group-label', label)
				$(el).attr('data-score', score)
				deselectWords()

	setPopupScore = (score) ->
		$popupChoices.removeClass('selected')
		$popupChoices.filter("[data-score=#{ score }]").addClass('selected')

	showWordScorePopup = (el) ->
		# TODO: link score to word, must switch over from labels... 
		$popup.addClass('visible').focus()
		$popup.find('.lemma').text($(el).attr('data-lemma'))
		setPopupScore($(el).attr('data-score'))
		$popupChoices.click (e) ->
			score = $(this).attr('data-score')
			if score >= 0 and score <= 5
				setPopupScore(score)
				updateWord(el, score)
		$(document).on 'keyup', (e) ->
			if e.keyCode == 27  # esc
				deselectWords()
		$(document).on 'keypress', (e) ->
			char = String.fromCharCode(e.keyCode)
			score = parseInt(char, 10)
			if score in SRS_SCORE_CHOICES
				$popup.find(".choice[data-score=\"#{ score }\"]").trigger('click')


	hideWordScorePopup = (el) ->
		$popup = $('#word-score-popup')
		$popup.removeClass('visible')
		$popupChoices.off 'click'
		$(document).off 'keyup keypress'

	attachAnnotationControls = ($el) ->
		$popup = $('#word-score-popup')
		$el.click (e) ->
			selectWord(this)

	attachAnnotationControls( $('.annotated-word-list li:not([data-group-label="ignored"])') )


$ ->
	setupAnnotation()

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