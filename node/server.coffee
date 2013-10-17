express = require 'express'
mongoose = require 'mongoose'
fs = require 'fs'

# database = (require './database')
# schema = require './schema'
# models = require './models'

# setup

app = express()
models = {}

mongoose.connect('mongodb://localhost/superglot')
conn = mongoose.connection
conn.on('error', console.error.bind(console, 'connection error:'));
conn.once 'open', ->
	console.log('mongodb connection opened')

	wordSchema = new mongoose.Schema
		reading: String
		language: String

	models =
		Word: mongoose.model 'Word', wordSchema, 'words'

	# loadFixtures()


loadFixtures = ->
	fs.readFile './data/corncob_lowercase.txt', 'ascii', (err, data) ->
		conn.collection('words').remove (err) ->
			sampleWords = data.split(/\r?\n/)
			wordFixtures = ({reading: w, language: 'en'} for w in sampleWords)
			models.Word.create wordFixtures, (err) ->
				console.log 'creation error: ', err if err?
			console.log sampleWords.length + ' fixtures loaded'


# routes

app.get '/user/words', (req, res) ->
	q = models.Word.find({language: 'en'})
	q.exec 'find', (err, data) ->
		res.send(data)


app.get '/hello.txt', (req, res) ->
  body = 'Hello World'
  res.setHeader('Content-Type', 'text/plain')
  res.setHeader('Content-Length', body.length)
  res.end(body)





# startup

app.listen(3000)
console.log('Listening on port 3000')