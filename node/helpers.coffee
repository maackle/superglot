
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
		res.json 401, 'must log in first'

exports.withDummyUser = (fn) ->
	models.User.findOne null, fn

