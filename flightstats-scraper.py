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
print(r.content)

# Command from: https://www.dataquest.io/blog/web-scraping-tutorial-python/

page = requests.get(url)
print(page)
#print(page.content)

from bs4 import BeautifulSoup
soup = BeautifulSoup(page.content, 'html.parser')
print(soup.prettify())

'''

filename = wget.download(url)
print(filename)

import urllib.request, urllib.error, urllib.parse

url = 'https://www.flightradar24.com/30.9,31.95/5'

response = urllib.request.urlopen(url)
webContent = response.read()

print(webContent[0:300])
'''
'''
metacount = 0


class MyHTMLParser(HTMLParser):
    def handle_comment(self, data):
        print("Encountered comment: ", data)
        pos = self.getpos()
        print("\tAt line:", pos[0], " position ", pos[1])

    def handle_starttag(self, tag, attrs):
        global metacount
        if tag == "meta":
            metacount += 1

        print("Encountered a start tag: ", tag)
        pos = self.getpos()
        print("\tAt line:", pos[0], " position ", pos[1])

        if attrs.__len__() > 0:
            print("\tAttributes:")
            for a in attrs:
                print("\t", a[0], "=", a[1])

    def handle_endtag(self, tag):
        print("Encountered tag: ", tag)
        pos = self.getpos()
        print("\tAt line:", pos[0], " position ", pos[1])

    def handle_data(self, data):
        if (data.isspace()):
            return
        print("Encountered data: ", data)
        pos = self.getpos()
        print("\tAt line:", pos[0], " position ", pos[1])


def main():
    # instantiate the parser and feed it some HTML
    parser = MyHTMLParser()
    f = open("samplehtml.html")
    if f.mode == 'r':
        contents = f.read()
        parser.feed(contents)
        print("%d Meta tags found: " % metacount)


if __name__ == "__main__":
    main();
'''