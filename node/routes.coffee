models = require './models'
fs = require 'fs'

exports.setup = (app, conn, passport) ->

	(require './routes/pages').setup app, conn, passport
	(require './routes/api').setup app, conn, passport
	(require './routes/auth').setup app, conn, passport

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
					console.error 'creation error: ', err if err?

			conn.collection('users').remove (err) ->
				userFixtures = [
					email: 'maackle.d@gmail.com'
					lemmata:
						known: sampleWords[0...10]
						learning: sampleWords[1000...1010]
				]
				models.User.create userFixtures, (err) ->
					console.error 'creation error' + err if err?

			conn.collection('documents').remove (err) ->

			models.Word.count (err, count) ->
				console.log "loaded fixtures: " + count + " words"
			res.json
				message: 'loaded words and fixtures'