express = require 'express'
mongoose = require 'mongoose'
fs = require 'fs'
_ = require 'underscore'

# database = (require './database')
schema = require './schema'
models = require './models'

# setup

app = express()
app.use(express.bodyParser())

mongoose.connect('mongodb://localhost/superglot')
conn = mongoose.connection
# conn.on('error', console.error.bind(console, 'connection error:'));
conn.once 'open', ->
	console.log('mongodb connection opened')

	# loadFixtures()


loadFixtures = ->
	fs.readFile './data/corncob_lowercase.txt', 'utf-8', (err, data) ->
		sampleWords = data.split(/\r?\n/)[1000..10000]
		
		conn.collection('words').remove (err) ->
			wordFixtures = ({
				reading: w
				lemma: w.toLowerCase()
				language: 'en'
			} for w in sampleWords)
			models.Word.create wordFixtures, (err) ->
				console.log 'creation error: ', err if err?

		conn.collection('users').remove (err) ->
			userFixtures = [
				email: 'maackle.d@gmail.com'
				words: sampleWords[0..100]
			]
			models.User.create userFixtures, (err) -> 
				console.log 'creation error' + err if err?


qfn = (fn) ->
	(err, model) -> 
		if err?
			console.error err
		else
			fn(model)

withUser = (fn) ->
	models.User.findOne null, qfn fn

# routes

app.get '/api/words', (req, res) ->
	models.Word
		.find({language: 'en'}, 'reading lemma')
		.exec qfn (words) ->
			res.send(words)

app.get '/api/user', (req, res) ->
	models.User.findOne null, (err, user) ->
		q = models.Word.find({language: 'en'})
		if err
			res.send(500, err)
		else
			res.send(user)

app.all '/api/user/lemmata/add', (req, res) ->
	lemma = req.body.lemma
	models.User.findOne null, (err, user) ->
		if err
			res.send(500, err)
		else
			user.lemmata.push lemma
			user.lemmata.sort()
			user.save()
			res.send
				lemma: lemma
				classification: 'sg-tracked'

app.all '/api/user/lemmata/remove', (req, res) ->
	models.User.findOne null, (err, user) ->
		if err
			res.send(500, err)
		else		
			lemma = req.body.lemma
			user.lemmata = user.lemmata.filter (l) -> l isnt lemma
			user.save()
			res.send
				lemma: lemma
				classification: 'sg-untracked'


app.get '/hello.txt', (req, res) ->
  body = 'Hello World'
  res.setHeader('Content-Type', 'text/plain')
  res.setHeader('Content-Length', body.length)
  res.end(body)

app.get '/dev/load-fixtures', (req, res) ->
	loadFixtures()
	res.send 'loaded words and users fixtures'




# startup

app.listen(3000)
console.log('Listening on port 3000')