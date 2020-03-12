"""
Module: Data Mining
Exercise: collecting data from flightstats
Author: Dor Meir & Itamar Bergfreund
Date: 12. March 2020
"""


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import csv


def create_list_of_airports(filename):
    """takes a list of all airports and filters it to get only medium and large airports with following information:

    ['ident', 'type', 'name', 'elevation_ft', 'continent', 'iso_country', 'iso_region', 'municipality',
    'gps_code', 'iata_code', 'local_code', 'coordinates']

    Airport data was taken from :https://ourairports.com/data/
    """

    with open(filename, 'r', encoding="utf-8") as d:
        data = csv.reader(d)
        airports = [row for row in data]
    print (airports[0])
    return [airport for airport in airports if airport[1] == 'large_airport' or airport[1] == 'medium_airport']


def get_iata_code(airports):
    """creates an array with iata-codes and deletes airports without a code"""

    return [airport[9] for airport in airports if airport[9] != '']


def collect_flight_links(url):
    """This function collects links of each flight from the airport specific web page"""

    driver = webdriver.Chrome()
    driver.get(url)

    S_TILL_TIMEOUT = 5

    # this loop clicks through the flights by clicking on the next button
    # and collects all the flight specific links until reaching the last page
    while True:
        try:
            driver.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(driver, S_TILL_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"__next\"]/div/section/div/div[2]/div[1]/div[3]/div/div/div[16]/span"))))
            driver.find_element_by_xpath("//*[@id=\"__next\"]/div/section/div/div[2]/div[1]/div[3]/div/div/div[16]/span").click()

            #todo: get links function

        except (TimeoutException, WebDriverException):
            break