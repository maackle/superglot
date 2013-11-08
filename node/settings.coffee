
_ = require 'lodash'

settings = 
	hi: 'hi'

module.exports = _.extend settings, (require './local/settings')