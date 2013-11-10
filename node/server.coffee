_ = require 'lodash'
fs = require 'fs'
url = require 'url'
path = require 'path'
compass = require 'node-compass'
express = require 'express'
flash = require 'express-flash'
mongoose = require 'mongoose'
MongoStore = require('connect-mongo')(express)

passport = require 'passport'
LocalStrategy = require('passport-local').Strategy
GoogleStrategy = require('passport-google-oauth').OAuth2Strategy

util = 		require '../common/util'
nlp = 		require '../common/nlp'
common = 	require '../common/common'
settings = 	require './settings'
database = 	require './database'
schema = 	require './schema'
models = 	require './models'
routes = 	require './routes'
{qfn, withDummyUser, requireUser} = require './helpers'

conn = database.connectLocal()
conn.once 'open', ->
	# startup
	console.log('mongodb connection opened')
	app.listen(3000)
	console.log('Listening on port 3000')
# conn.on('error', console.error.bind(console, 'connection error:'));

# setup
app = express()
app.use express.bodyParser()
app.use express.cookieParser settings.COOKIE_SECRET
app.use flash()
app.use express.session
	secret: 'osijdfo8'
	maxAge: 60000
	store: new MongoStore
        db: conn.db

app.use compass
	sass: 'stylesheets'
	css: 'static/css'
	project: __dirname
	logging: true
app.use '/static', express.static __dirname + '/static'
app.use passport.initialize()
app.use passport.session()

app.use (req, res, next) ->
	user = req.user
	if user?
		user.lemmaCounts =
			known: user.lemmata.known.length
			learning: user.lemmata.learning.length
			ignored: user.lemmata.ignored.length
	res.locals.user = user
	next()

# app.set 'views', __dirname + '/views'
# app.engine 'jade', require('jade').__express


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
	done null, user.id

passport.deserializeUser (id, done) ->
	models.User.findById id, (err, user) ->
		done null, user


routes.setup app, conn, passport
