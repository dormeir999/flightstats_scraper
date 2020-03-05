#
# Example file for parsing and processing HTML
#
from html.parser import HTMLParser
import requests

#response = requests.get('https://www.flightradar24.com/30.9,31.95/5')
#print(response.status_code)

#import wget
import requests
#import json
myProxy = {"http"  : "http://10.120.118.49:8080", "https"  : "https://10.120.118.49:8080"}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}
url = 'https://www.flightstats.com/v2/flight-tracker/departures/zrh'

s = requests.session()
r = s.get(url)#, proxies = myProxy, headers = headers)
#print(r.content)

# Command from: https://www.dataquest.io/blog/web-scraping-tutorial-python/

page = requests.get(url)
#print(page)
#print(page.content)

from bs4 import BeautifulSoup
soup = BeautifulSoup(page.content, 'html.parser')
#print(soup.prettify())


# select all the elements at the top level of the page
#print(list(soup.children))

# Let’s see what the type of each element in the list is:
#[type(item) for item in list(soup.children)]

#We can now select the html tag and its children by taking the third item in the list:
html = list(soup.children)[1]

# Now, we can find the children inside the html tag:
#print(list(html.children))

# we want to extract the text of flights, so we’ll dive into the body, which is the second (out of 2) tags:
body = list(html.children)[1]

# Now, we can get the children of the body tag:
list(body.children)

# There are 8 children:
print(len(list(body.children)))

# This child contains the next page:

# This child contains the next page:
print(list(body.children)[4])
