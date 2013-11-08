
mongoose = require 'mongoose'
settings = require './local/settings'

exports.connectRemote = ->
	uri = settings.MONGOLAB_URI
	mongoose.connect uri,
		user: settings.MONGOLAB_USER
		pass: settings.MONGOLAB_PASS
	mongoose.connection

exports.connectLocal = ->
	mongoose.connect('mongodb://localhost/superglot')
	mongoose.connection