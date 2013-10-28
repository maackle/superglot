
if exports?
	util = require('./util')
else
	util = window.util


enums = 
	KINDS: [
		'known'
		'learning'
		'ignored'
		'common'
		'untracked'
	]
	USER_KINDS: [
		'known'
		'learning'
		'ignored'
	]
	STATIC_KINDS: [
		'common'
		'invalid'
	]


class DocumentInfo  # currently unused

	language: 'en'

	constructor: ({@stats}) ->


class LemmaPartition

	language: 'en'
	known: null
	learning: null
	ignored: null

	constructor: ({@known, @learning, @untracked}) ->
		@ignored = "the be to of and a in that have i it for not on with he she him her his hers as you do at this but by from they we or an will my would there their what so its is".split(' ')

	applyDiff: (diff) ->
		console.assert diff.removeFrom? and diff.addTo?
		source = @[diff.removeFrom]  # ignoring source for now, to be more consistent (though slower)
		target = @[diff.addTo]
		lemmata = diff.lemmata
		for kind in enums.USER_KINDS
			source = @[kind]
			for i in (util.binarysearch source, lemma for lemma in lemmata) when i >= 0
				source.splice i, 1
			# source = _.without source, lemmata
		if target?
			target = target.concat lemmata
			target.sort()
		@[diff.removeFrom] = source
		@[diff.addTo] = target

	getIntersections: (lemmata) ->
		intersect = (list, words) ->
			ixs = (util.multiBinarySearch list, words)
			words.filter (w, i) -> ixs[i] >= 0

		known: intersect @known, lemmata
		learning: intersect @learning, lemmata
		ignored: intersect @ignored, lemmata


class LemmaDiff

	constructor: ({@removeFrom, @addTo, @lemmata}) ->

	idempotent: () -> (@addTo == @removeFrom) or @lemmata.length == 0

(exports ? window).LemmaPartition = LemmaPartition
(exports ? window).LemmaDiff = LemmaDiff
(exports ? window).enums = enums