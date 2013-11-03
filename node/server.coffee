

_ = require 'underscore'
fs = require 'fs'
url = require 'url'
path = require 'path'
compass = require 'node-compass'
express = require 'express'
flash = require 'express-flash'
mongoose = require 'mongoose'

passport = require 'passport'
LocalStrategy = require('passport-local').Strategy
GoogleStrategy = require('passport-google-oauth').OAuth2Strategy

util = 		require '../common/util'
nlp = 		require '../common/nlp'
common = 	require '../common/common'
settings = 	require './local/settings'
database = 	require './local/database'
schema = 	require './schema'
models = 	require './models'

# setup
app = express()
app.use express.bodyParser()
app.use express.cookieParser settings.COOKIE_SECRET
app.use express.session cookie: maxAge: 60000
app.use flash()
app.use compass
	sass: 'stylesheets'
	css: 'static/css'
	project: __dirname
	logging: true
app.use '/static', express.static __dirname + '/static'
app.use passport.initialize()
app.use passport.session()
app.use (req, res, next) ->
	res.locals.user = req.user
	next()
# app.set 'views', __dirname + '/views'
# app.engine 'jade', require('jade').__express

conn = database.connectRemote()
conn.once 'open', ->
	console.log('mongodb connection opened')
# conn.on('error', console.error.bind(console, 'connection error:'));

passport.use new LocalStrategy (username, password, done) ->
	models.User.findOne (email: username), (err, user) ->
		if err then return done(err)
		else if not user then return done null, false, message: "email not found: #{ username }"
		else
			return done null, user

passport.use new GoogleStrategy
	clientID: settings.GOOGLE_OAUTH_CLIENT_ID,
	clientSecret: settings.GOOGLE_OAUTH_CLIENT_SECRET,
	callbackURL: url.resolve settings.ROOT_URL, settings.GOOGLE_RETURN_URI
, (accessToken, refreshToken, profile, done) ->
	console.log accessToken, refreshToken, profile, done
	models.User.findOne googleToken: accessToken, (err, user) ->
		if err
			email = profile.emails[0]
			models.User.create 
				email: email
				googleToken: accessToken
			, (err, user) ->
				done(err, user)
		else
			done(err, user)

passport.serializeUser (user, done) ->
	console.log user.id
	done null, user.id

passport.deserializeUser (id, done) ->
	console.log 'id:', id
	models.User.findById id, (err, user) ->
		console.log err, user
		done null, user

qfn = (fn) ->
	(err, data) -> 
		if err?
			console.error err
		else
			fn(data)

withUser = (fn) ->
	models.User.findOne null, fn


#######################################
## routes

app.get '/', (req, res) ->
	res.render('home.jade')

app.get '/login', (req, res) ->
	res.render('auth/login.jade')

app.post '/login', passport.authenticate 'local',
	successRedirect: '/'
	failureRedirect: '/login'
	failureFlash: true

app.get '/logout', (req, res) ->
	req.logout()
	res.redirect '/'

app.get '/api/words/lemmata', (req, res) ->
	models.Word
		.find({language: 'en'}, 'lemma')
		.sort('lemma')
		.exec qfn (words) ->
			res.json
				all: words.map (w) -> w.lemma
				common: "i you am a the he she it we they him her".split(' ').sort()

app.get '/api/user', (req, res) ->
	models.User.findOne null, (err, user) ->
		if err
			res.send(500, err)
		else
			res.json(user)
	
	# TODO
	# chrome.cookies.get 
	# 	url: 'http://superglot.com'
	# 	name: 'connect.sid'
	# , (cookie) ->
	# 	console.log 'READ THE COOKIE', cookie

app.get '/auth/google', passport.authenticate 'google', scope: 'email'

app.get '/auth/google/callback', passport.authenticate('google', failureRedirect: '/login'), (req, res) ->
	res.redirect('/')


app.post '/api/user/words/apply-diffs', (req, res) ->
	withUser (err, user) ->
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
				lemmata: 
					known: sampleWords[0...10]
					learning: sampleWords[1000...1010]
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