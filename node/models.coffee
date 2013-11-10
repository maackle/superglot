
mongoose = require 'mongoose'
schema = require './schema'

exports.Word = mongoose.model 'Word', schema.word, 'words'
exports.User = mongoose.model 'User', schema.user, 'users'
exports.Document = mongoose.model 'Document', schema.document, 'documents'