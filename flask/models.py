from flask import session
from mongoengine import *
from flask.ext.login import UserMixin

# class DictBackedObject(object):

# 	collection = None

# 	def __init__(self, data={}, **kwargs):
# 		# self._data = data
# 		for key, val in data.items():
# 			setattr(self, key, val)
# 		for key, val in kwargs.items():
# 			setattr(self, key, val)

# 	def save(self):
# 		self.collection.save(self.__dict__)

email_field = StringField(max_length=128, required=True)
lemmata_field = ListField(StringField(max_length=256))

class User(Document, UserMixin):

	email = email_field
	password = StringField(max_length=32, required=True)
	lemmata = lemmata_field

	def get_id(self):
		return str(self.id)

	@staticmethod
	def authenticate(email, password):
		user = User.objects(email=email, password=password).first()
		return user

class Word(Document):

	reading = StringField(max_length=128)
	lemma = StringField(max_length=128)
	language = StringField(max_length=8)


class TextArticle(Document):
	
	title = StringField(max_length=256)
	plaintext = StringField()
	lemmata = lemmata_field
	source = StringField()