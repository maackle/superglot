
# haystack must be sorted
binarysearch = (haystack, needle) ->
	l = 0
	u = haystack.length
	m = undefined
	while l <= u
		if needle > haystack[(m = Math.floor((l + u) / 2))]
			l = m + 1
		else
			u = (if (needle is haystack[m]) then -2 else m - 1)
	(if (u is -2) then m else -1)

# haystack and needles must both be sorted
multiBinarySearch = (haystack, needles) ->
	l = lastHit = -1
	for needle in needles
		l = lastHit
		m = undefined
		u = haystack.length
		while l <= u
			if needle > haystack[(m = Math.floor((l + u) / 2))]
				l = m + 1
			else
				u = (if (needle is haystack[m]) then -2 else m - 1)
		if (u is -2)
			lastHit = m
			m
		else
			-1


if exports?
	exports.binarysearch = binarysearch
	exports.multiBinarySearch = multiBinarySearch
else
	window.util = 
		binarysearch: binarysearch
		multiBinarySearch: multiBinarySearch