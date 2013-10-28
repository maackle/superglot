
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


class LemmaPartition

	language: 'en'
	known: null
	learning: null
	ignored: null

	constructor: ({@known, @learning, @untracked}) ->
		@ignored = "the be to of and a in that have i it for not on with he she him her his hers as you do at this but by from they we or an will my would there their what so its".split(' ')

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

	getCounts: (lemmata) ->
		count = (list, words) ->
			(util.multiBinarySearch list, words).filter (i) -> i >= 0
			
		known: count known, lemmata
		learning: count learning, lemmata
		ignored: count ignored, lemmata


class LemmaDiff

	constructor: ({@removeFrom, @addTo, @lemmata}) ->

	idempotent: () -> (@addTo == @removeFrom) or @lemmata.length == 0

(exports ? window).LemmaPartition = LemmaPartition
(exports ? window).LemmaDiff = LemmaDiff
(exports ? window).enums = enums