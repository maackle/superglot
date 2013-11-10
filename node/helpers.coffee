
models = require './models'

exports.qfn = (fn) ->
	(err, data) ->
		if err?
			console.error err
		else
			fn(data)

exports.requireUser = (req, res, next) ->
	if req.user
		next()
	else
		req.flash 'warn', 'Please log in first'
		res.redirect '/login'

exports.withDummyUser = (fn) ->
	models.User.findOne null, fn

