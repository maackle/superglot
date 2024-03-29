SRS_RATING_CHOICES = [1,2,3,4]  # the ratings that can be selected by pressing the keypad

markWords = (lemmata, rating, after) ->
	if rating == 'known'
		rating = 4
	else if rating == 'learning'
		rating = 2

	rating = parseInt(rating, 10)

	lemmataString = lemmata.join("\n")
	$.post '/api/user/words/update/', {
		lemmata: lemmataString
		rating: rating
	}, after

addMeaningTooltip = (el, meaning) ->
	$(el).tooltip
		title: meaning
		placement: 'left'

setupAnnotation = ->
	$popup = $('#word-rating-popup')
	$popupChoices = $popup.find('.ratings .choice')

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

	updateWord = (el, rating) ->
		lemma = $(el).attr('data-lemma')
		markWords [lemma], rating, (data) ->
			if data
				$set = $(".word[data-lemma='#{ lemma }']")
				$set.attr('data-rating', rating)
				deselectWords()

	setPopupScore = (rating) ->
		$popupChoices.removeClass('selected')
		$popupChoices.filter("[data-rating=#{ rating }]").addClass('selected')

	showWordScorePopup = (el) ->
		# TODO: link rating to word, must switch over from labels...
		$popup.addClass('visible').focus()
		$popup.find('.lemma').text($(el).attr('data-lemma'))
		setPopupScore($(el).attr('data-rating'))
		$popupChoices.click (e) ->
			rating = parseInt($(this).attr('data-rating'), 10);
			setPopupScore(rating)
			updateWord(el, rating)
		$(document).on 'keyup', (e) ->
			if e.keyCode == 27  # esc
				deselectWords()
		$(document).on 'keypress', (e) ->
			char = String.fromCharCode(e.keyCode)
			rating = parseInt(char, 10)
			if rating in SRS_RATING_CHOICES
				$popup.find(".choice[data-rating=\"#{ rating }\"]").trigger('click')


	hideWordScorePopup = (el) ->
		$popup = $('#word-rating-popup')
		$popup.removeClass('visible')
		$popupChoices.off 'click'
		$(document).off 'keyup keypress'

	attachAnnotationControls = ($el) ->
		$popup = $('#word-rating-popup')
		$el.click (e) ->
			selectWord(this)

	attachAnnotationControls( $('.annotated-words .word:not([data-rating="-1"])') )


$ ->
	setupAnnotation()

	$('.annotated-words .controls .mark-all').click (e) ->
		label = $(this).attr('data-group-label')
		$affected = $('.annotated-words .word')
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