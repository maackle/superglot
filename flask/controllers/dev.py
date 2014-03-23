from flask import Blueprint, render_template, request

from database import db

@blueprint.route('/schemify')
def schemify():
	return 'API v1.0'
