
mongoose = require 'mongoose'
schema = require './schema'

exports.Word = mongoose.model 'Word', schema.word