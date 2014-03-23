from pymongo import MongoClient

mongo_client = MongoClient('mongodb://localhost/superglot')
db = mongo_client.superglot

db.users.create_index('email', unique=True)
db.users.create_index('lemmata', unique=True)