from flask import Blueprint, render_template, request

@blueprint.route('/schemify')
def schemify():
	return 'API v1.0'
