from bs4 import BeautifulSoup
import requests

from cache import cache

@cache.memoize()
def get_remote_text(url):
	req = requests.get(url)
	soup = BeautifulSoup(req.text)
	text = soup.get_text()
	return text