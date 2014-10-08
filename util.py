import sys
from bs4 import BeautifulSoup
import requests
from collections import defaultdict
import datetime

from cache import cache

now = datetime.datetime.now

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]


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
		percents[label] = 100 * counts[label] / total_significant

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