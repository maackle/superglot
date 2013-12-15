htmlparser = require 'htmlparser2'
request = require 'request'

nlp = require '../../common/nlp'
models = require '../models'
helpers = require '../helpers'
documents =
	forms: require '../views/user/documents/forms'

makeDocument = (form, fn) ->
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

	make = ({title, plaintext, source}) ->
		lemmata = NLP.lemmatize NLP.segment plaintext
		console.log 'aaarg', arguments
		console.log 'emmmmala', lemmata
		models.Document.create
			title: title
			lemmata: lemmata
			plaintext: plaintext
			source: source
		, fn

	descriptor = null

	if body?
		{title, body} = form.data
		descriptor = 
			title: title
			source: null
			plaintext: body
	else if url
		source = url
		request url, (err, res, body) ->
			if err
				console.error err
				return null
			else
				parser.write body  # updates plaintext
				parser.end()
				
				descriptor = 
					title: title
					plaintext: plaintext
					source: source
	else
		console.error "no source for document"

	if descriptor?
		doc = make descriptor, fn
	else
		console.error "no descriptor"


exports.setup = (app, conn) ->

	app.get '/', (req, res) ->
		if req.user then res.render('dashboard.jade')
		else
			res.render('home.jade')

	app.get '/words', helpers.requireUser, (req, res) ->
		res.render('user/words.jade')

	app.get '/documents', helpers.requireUser, (req, res) ->
		form = documents.forms.add
		models.Document.find (err, docs) ->
			console.log "finding", err, docs
			res.render 'user/documents.jade',
				formHTML: form.toHTML()
				documents: docs

	app.post '/documents', helpers.requireUser, (req, res) ->
		form = documents.forms.add
		form.handle req,
			success: (form) ->
				doc = makeDocument form, (err, doc) ->
					if err
						console.error "problem creating document"
						req.flash 'error', 'problem creating document'
					else
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