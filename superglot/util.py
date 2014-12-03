import sys
from bs4 import BeautifulSoup
import requests
from collections import defaultdict
import datetime
from flask import url_for

from superglot.cache import cache

now = datetime.datetime.now

def chunks(l, n):
	""" Yield successive n-sized chunks from l.
	"""
	for i in range(0, len(l), n):
		yield l[i:i+n]

def dict_from_seq(s, mapper=None):
	if mapper:
		t = map(mapper, s)
	else:
		t = s
	return dict(zip(t, s))

def multi_dict_from_seq(s, mapper=None):
	if mapper:
		t = map(mapper, s)
	else:
		t = s
	d = defaultdict(list)
	for k, v in zip(t, s):
		d[k].append(v)
	return d

@cache.memoize()
def get_page(url):
	req = requests.get(url)
	return req

def string_hash(s):
	'''
	Creates a reasonable hash value for a string
	'''
	return sum([ord(ch)*31 for ch in s])


def sorted_words(words):
	return sorted(words, key=lambda word: word.reading.lower())


def vocab_stats(vocab):

	counts = defaultdict(int)
	percents = defaultdict(int)

	for item in vocab:
		counts[item.label] += 1

	total = len(vocab)
	total_significant = total - counts['ignored']

	for label in counts:
		percents[label] = 100 * counts[label] / (total_significant or 1)

	return {
		'counts': counts,
		'percents': percents,
		'total_significant': total_significant,
		'total': total,
	}


def get_remote_article(url):

	forbidden_tags = ['script', 'code', 'head']

	req = get_page(url)
	soup = BeautifulSoup(req.text)

	title = soup.title.string if soup.title else url

	for tag in forbidden_tags:
		for t in soup(tag):
			t.decompose()

	text = "\n".join(soup.stripped_strings)

	# for tag in soup.find_all(allowed_tags):
	# 	text += ' ' + tag.text
	return (text, title)

def get_site_links(app):
	links = []
	for rule in app.url_map.iter_rules():
		# Filter out rules we can't navigate to in a browser
		# and rules that require parameters
		print(rule.endpoint, '||', rule.defaults, '||', rule.arguments)
		if "GET" in rule.methods and len(rule.defaults or []) >= len(rule.arguments):
			url = url_for(rule.endpoint)
			links.append((url, rule))
	return links


def random_string(N):
	import random
	import string
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

import time

class Timer(object):
	def __init__(self, verbose=False):
		self.verbose = verbose

	def __enter__(self):
		self.start = time.time()
		return self

	def __exit__(self, *args):
		self.end = time.time()
		self.secs = self.end - self.start
		self.msecs = self.secs * 1000  # millisecs
		if self.verbose:
			print('elapsed time: %f ms' % self.msecs)