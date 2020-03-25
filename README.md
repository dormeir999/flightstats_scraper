# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* Flightstats_scaper is a webscraper that collects departure and flight data from big and medium airports around the world form the https://www.flightstats.com/ website.

* Version 1.3

### Requierments: ###

* Python 3

Python Libaries:
* selenium
* bs4 (BeautifulSoup)
* requests
* re
* csv
* sys
* os

Webbrowser:
The program uses Chrome as a browser. For Selenium to work a WebDriver needs to be intalled:
Instructions: https://selenium-python.readthedocs.io/installation.html
Download: https://sites.google.com/a/chromium.org/chromedriver/downloads

Data:
Airport data was taken from: https://ourairports.com/data/airports.csv"


### Deployment: ###

Run flightstats-scraper.py with the airpot data csv file as argument:
python3 flightstats-scraper.py airports.csv

### Testing: ###

Before performing the scrape the scraper will first try to fetch the recent flights from the Hartsfield–Jackson Atlanta International Airport - The busiest airport in the world. 
If this succeeds, it will move on to scraping the supplied airport data csv file.

