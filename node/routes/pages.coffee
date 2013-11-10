htmlparser = require 'htmlparser2'
request = require 'request'

nlp = require '../../common/nlp'
models = require '../models'
helpers = require '../helpers'
documents =
	forms: require '../views/user/documents/forms'

makeDocument = (form) ->
	{title, url, body} = form.data
	plaintext = ''
	source = null
	NLP = new nlp.NLP

	parser = new htmlparser.Parser
		ontext: (text) ->
			plaintext += text + " "
		onclosetag: (tagname) ->
			if tagname in ['div', 'script', 'section', 'p']
				plaintext += "\n"

		onend: ->

	make = ({title, lemmata, plaintext, source}) ->
		models.Document.create
			title: title
			lemmata: lemmata
			plaintext: plaintext
			source: source


	if body
		source = null
		plaintext = body
		make form.data
	else if url
		source = url
		request url, (err, res, body) ->
			if err
				console.error err
				return null
			else
				parser.write body  # updates plaintext
				parser.end()

				lemmata = NLP.lemmatize NLP.segment plaintext
				make
					title: title
					lemmata: lemmata
					source: source
					plaintext: plaintext

				console.log "TIT", title, source
				console.log lemmata


exports.setup = (app, conn) ->

	app.get '/', (req, res) ->
		if req.user then res.render('dashboard.jade')
		else
			res.render('home.jade')

	app.get '/words', helpers.requireUser, (req, res) ->
		res.render('user/words.jade')

	app.get '/documents', helpers.requireUser, (req, res) ->
		form = documents.forms.add
		res.render 'user/documents.jade',
			formHTML: form.toHTML()

	app.post '/documents', helpers.requireUser, (req, res) ->
		form = documents.forms.add
		form.handle req,
			success: (form) ->
				doc = makeDocument form

				req.flash 'success', 'added a document'
				res.redirect '/documents'
			error: (form) ->
				res.render 'user/documents.jade',
					formHTML: form.toHTML()
			empty: (form) ->
				res.render 'user/documents.jade',
					formHTML: form.toHTML()

		# if req.body and req.body.title and (req.body.url or req.body.body)
		# 	req.flash('success', 'added a document')
		# else
		# 	if not req.body.title then req.flash 'error', 'Please enter a title'
		# 	if not (req.body.url or req.body.body) then req.flash 'error', 'Please enter the full text of a document or the URL of one'
		# res.locals.boundform = req.body or {}
		# res.redirect('/documents')