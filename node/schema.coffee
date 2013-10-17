
mongoose = require 'mongoose'

exports.word = new mongoose.Schema
	reading: String
	language: String

