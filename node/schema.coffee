
mongoose = require 'mongoose'

exports.word = new mongoose.Schema
	reading: String
	language: String

exports.user = new mongoose.Schema
	email: String
	words: [String]