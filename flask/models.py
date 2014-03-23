from flask import session
from flask.ext.login import UserMixin
from bson.objectid import ObjectId

from database import db

users = db.users

class DictBackedObject(object):

	collection = None

	def __init__(self, data={}, **kwargs):
		# self._data = data
		for key, val in data.items():
			setattr(self, key, val)
		for key, val in kwargs.items():
			setattr(self, key, val)

	def save(self):
		self.collection.save(self.__dict__)


class User(UserMixin, DictBackedObject):

	collection = db.users

	def __init__(self, email, password, lemmata=[], **kwargs):
		super().__init__(email=email, password=password, lemmata=set(lemmata), **kwargs)

	def get_id(self):
		return str(self._id)

	def save(self):
		data = self.__dict__
		data['lemmata'] = list(data['lemmata'])
		self.collection.save(data)

	@staticmethod
	def get(uid):
		data = users.find_one(ObjectId(uid))
		return User(**data)

	@staticmethod
	def authenticate(email, password):
		data = users.find_one({
			'email': email,
			'password': password,
			})
		if data:
			return User(**data)
		else:
			return None

	@staticmethod
	def create(email, password):
		return users.insert({
			'email': email,
			'password': password,
			'lemmata': [],
			})


class Word(DictBackedObject):
	pass
	# def __init__(self, reading, lemma, language):
	# 	super().__init__(reading, lemma, language, **kwargs)


class Document(DictBackedObject):
	pass
	# def __init__(self, title, plaintext, lemmata, source):
	# 	super().__init__(title, plaintext, lemmata, source, **kwargs)