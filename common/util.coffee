
binarysearch = (a, o) ->
	l = 0
	u = a.length
	m = undefined
	while l <= u
		if o > a[(m = Math.floor((l + u) / 2))]
			l = m + 1
		else
			u = (if (o is a[m]) then -2 else m - 1)
	(if (u is -2) then m else -1)

window?.util = {}
(exports ? util).binarysearch = binarysearch