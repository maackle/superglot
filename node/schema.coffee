
mongoose = require 'mongoose'

exports.word = new mongoose.Schema
	reading: String
	lemma: String
	language: String

exports.user = new mongoose.Schema
	email: String
	googleToken: String
	lemmata: 
		known: [String]
		learning: [String]
		ignored: [String]