# Flights stats scraper during Covid-19 #

POC of the Project:
https://docs.google.com/presentation/d/1sIZYruUzLq0ge70ACb_Ux8AyxM_FX4rozimYFW2nai4/edit?usp=sharing

The final dashboard:
![alt text](https://github.com/dormeir999/flightstats_scraper/blob/master/photos/1.png)

Some visualizations:
![alt text](https://github.com/dormeir999/flightstats_scraper/blob/master/photos/unnamed.png)
![alt text](https://github.com/dormeir999/flightstats_scraper/blob/master/photos/unnamed%20(1).png)


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

### Database Design: ###

/***

|-------------|------------|------------|----------|-------------|------------|
|  __FIELD__  |  __TYPE__  | __NULL__   | __KEY__  | __DEFAULT__ | __EXTRA__  |
|-------------|------------|------------|----------|-------------|------------|
| id.         | INT [PK]   |            |          |             |            |
| name        | VARCHAR    |            |          |             |            |
| type        | VARCHAR    |            |          |             |            |
| elevation_ft| INTEGER    |            |          |             |            |
| continent   | VARCHAR    |            |          |             |            |
| iso_country | VARCHAR    |            |          |             |            |
| iso_region  | VARCHAR    |            |          |             |            |
| municipality| VARCHAR    |            |          |             |            |
| gps_code    | VARCHAR    |            |          |             |            |
| iata_code   | VARCHAR    |            |          |             |            |
| local_code  | VARCHAR    |            |          |             |            |
| longitude   | FLOAT      |            |          |             |            |
| latitude    | FLOAT      |            |          |             |            |
***/
