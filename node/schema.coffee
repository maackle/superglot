
bcrypt = require 'bcrypt'
mongoose = require 'mongoose'

settings = 	require './local/settings'

word = new mongoose.Schema
	reading: String
	lemma: String
	language: String

user = new mongoose.Schema
	email: String
	googleId: String
	googleToken: String
	lemmata: 
		known: [String]
		learning: [String]
		ignored: [String]

user.methods.checkPassword = (password) ->
	"TODO"

exports.word = word
exports.user = user