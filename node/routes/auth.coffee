models = require '../models'

exports.setup = (app, conn, passport) ->

	app.get '/login', (req, res) ->
		res.render('auth/login.jade')

	app.post '/login', passport.authenticate 'local',
		successRedirect: '/'
		failureRedirect: '/login'
		failureFlash: true

	app.get '/logout', (req, res) ->
		req.logout()
		res.redirect '/'

	app.get '/auth/google', passport.authenticate 'google', scope: 'email'

	app.get '/auth/google/callback', passport.authenticate('google', failureRedirect: '/login'), (req, res) ->
		res.redirect('/')
