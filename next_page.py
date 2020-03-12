"""
Module: Data Mining
Exercise: collecting links from flightstats
Author: Dor Meir & Itamar Bergfreund
Date: 11. March 2020
"""


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


def collect_flight_links(url):
    """This function collects links of each flight from the airport specific web page"""

    driver = webdriver.Chrome()
    driver.get(url)

    # this loop clicks through the flights by clicking on the next button
    # and collects all the flight specific links until reaching the last page
    while True:
        try:
            driver.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"__next\"]/div/section/div/div[2]/div[1]/div[3]/div/div/div[16]/span"))))
            driver.find_element_by_xpath("//*[@id=\"__next\"]/div/section/div/div[2]/div[1]/div[3]/div/div/div[16]/span").click()

            #todo: get links function

        except (TimeoutException, WebDriverException):
            break


def main():
    url= 'https://www.flightstats.com/v2/flight-tracker/departures/zrh'
    collect_flight_links(url)


if __name__ == "__main__":
    main()

