from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

class Language(models.Model):

	name = models.CharField(max_length=64)
	code = models.CharField(max_length=3)


class PartOfSpeech(models.Model):

	name = models.CharField(max_length=32)


class Document(models.Model):

	title = models.CharField(max_length=128)
	language = models.ForeignKey('Language')
	body = models.TextField()


class Word(models.Model):

	reading = models.CharField(max_length=256)
	language = models.ForeignKey('Language')
	pos = models.ForeignKey('PartOfSpeech')

	def __str__(self):
		return "Word<{0}>".format(self.reading)


class Meaning(models.Model):

	text = models.TextField()
	word = models.ForeignKey('Word')
	language = models.ForeignKey('Language')

	def __str__(self):
		return "Meaning<{1}, {0}>".format(self.word.reading, self.language.code)


class User(AbstractUser):

	class Meta:
		unique_together = ('email', )
