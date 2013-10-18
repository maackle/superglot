express = require 'express'
mongoose = require 'mongoose'
fs = require 'fs'

# database = (require './database')
schema = require './schema'
models = require './models'

# setup

app = express()

mongoose.connect('mongodb://localhost/superglot')
conn = mongoose.connection
# conn.on('error', console.error.bind(console, 'connection error:'));
conn.once 'open', ->
	console.log('mongodb connection opened')

	# loadFixtures()
	console.log conn.collection('users').find()


loadFixtures = ->
	fs.readFile './data/corncob_lowercase.txt', 'utf-8', (err, data) ->
		sampleWords = data.split(/\r?\n/)[1000..10000]
		
		conn.collection('words').remove (err) ->
			wordFixtures = ({reading: w, language: 'en'} for w in sampleWords)
			models.Word.create wordFixtures, (err) ->
				console.log 'creation error: ', err if err?

		conn.collection('users').remove (err) ->
			userFixtures = [
				email: 'maackle.d@gmail.com'
				words: sampleWords[0..1000]
			]
			models.User.create userFixtures, (err) -> 
				console.log 'creation error' + err if err?

		console.log sampleWords.length + ' word fixtures loaded'


# routes

app.get '/users/:id', (req, res) ->
	userId = parseInt req.params.id
	models.User.findOne null, (err, user) ->
		q = models.Word.find({language: 'en'})
		if err
			res.send(500, err)
		else
			res.send(user)


app.get '/hello.txt', (req, res) ->
  body = 'Hello World'
  res.setHeader('Content-Type', 'text/plain')
  res.setHeader('Content-Length', body.length)
  res.end(body)





# startup

app.listen(3000)
console.log('Listening on port 3000')