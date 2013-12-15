forms = require 'forms'
fields = forms.fields

add = forms.create
	title: fields.string
		required: true
	url: fields.string()
	body: fields.string
		required: true
		widget: forms.widgets.textarea()

exports.add = add