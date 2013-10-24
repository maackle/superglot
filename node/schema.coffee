
mongoose = require 'mongoose'

exports.word = new mongoose.Schema
	reading: String
	lemma: String
	language: String

exports.user = new mongoose.Schema
	email: String
	lemmata: 
		known: [String]
		learning: [String]
		ignored: [String]