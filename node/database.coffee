mongoose = require 'mongoose'

mongoose.connect('localhost', 'superglot')
db = mongoose.connection
db.on('error', console.error.bind(console, 'connection error:'));
db.once 'open', ->
	console.log('mongodb connection opened')

exports.connection = db