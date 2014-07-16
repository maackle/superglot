import sys
from bs4 import BeautifulSoup
import requests

from cache import cache

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