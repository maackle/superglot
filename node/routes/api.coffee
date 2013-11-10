models = require '../models'

exports.setup = (app, conn, passport) ->

	app.get '/api/words/lemmata', (req, res) ->
		models.Word
			.find({language: 'en'}, 'lemma')
			.sort('lemma')
			.exec qfn (words) ->
				res.json
					all: words.map (w) -> w.lemma
					common: "i you am a the he she it we they him her".split(' ').sort()

	app.get '/api/user', (req, res) ->
		res.json(req.user or null)

	app.post '/api/user/words/apply-diffs', (req, res) ->
		withDummyUser (err, user) ->
			if err
				res.send(500, err)
			else
				lemmata = new common.LemmaPartition user.lemmata
					# known: user.lemmata.known
					# learning: user.lemmata.learning
					# ignored: user.lemmata.ignored
				for diff in JSON.parse req.body.diffs
					lemmata.applyDiff diff
				user.lemmata = lemmata
				user.save()
				res.json true

