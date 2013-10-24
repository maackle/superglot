express = require 'express'
mongoose = require 'mongoose'
fs = require 'fs'
_ = require 'underscore'

# database = (require './database')
util = require '../common/util'
nlp = require '../common/nlp'
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


qfn = (fn) ->
	(err, model) -> 
		if err?
			console.error err
		else
			fn(model)

withUser = (fn) ->
	models.User.findOne null, qfn fn


#######################################
## routes

app.get '/api/words', (req, res) ->
	# res.json [
	# 	'walrus'
	# 	'forget'
	# ].map (l) -> {lemma: l}
	# return
	models.Word
		.find({language: 'en'}, 'reading lemma')
		# .limit(10000)
		.exec qfn (words) ->
			res.json(words)

app.get '/api/user', (req, res) ->
	models.User.findOne null, (err, user) ->
		if err
			res.send(500, err)
		else
			res.json(user)

app.post '/api/user/words/add', (req, res) ->
	lemma = req.body.lemma
	models.User.findOne null, (err, user) ->
		if err
			res.send(500, err)
		else
			if util.binarysearch(user.lemmata, lemma) < 0
				user.lemmata.push lemma
				user.lemmata.sort()
				user.save()
			res.json
				lemma: lemma
				classification: 'sg-known'

app.post '/api/user/words/remove', (req, res) ->
	models.User.findOne null, (err, user) ->
		if err
			res.send(500, err)
		else		
			lemma = req.body.lemma
			if util.binarysearch(user.lemmata, lemma) >= 0
				user.lemmata = user.lemmata.filter (l) -> l isnt lemma
				user.save()
			res.json
				lemma: lemma
				classification: 'sg-untracked'

app.get '/dev/load-fixtures', (req, res) ->
	fs.readFile './data/corncob_lowercase.txt', 'utf-8', (err, data) ->
		sampleWords = data.split(/\r?\n/)#[1000..10000]
		
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
				lemmata: sampleWords[0..100]
			]
			models.User.create userFixtures, (err) -> 
				console.log 'creation error' + err if err?

		models.Word.count (err, count) ->
			console.log "loaded fixtures: " + count + " words"
		res.json 
			message: 'loaded words and fixtures'




# startup

app.listen(3000)
console.log('Listening on port 3000')