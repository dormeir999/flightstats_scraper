"""
Module: Data Mining
Exercise: collecting links from flightstats
Author: Dor Meir & Itamar Bergfreund
Date: 18. March 2020
"""


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import platform
import requests
from bs4 import BeautifulSoup



def collect_flight_links(url):
    """
    This function collects links of each flight from the airport specific web page using pagination.
    :param url: airport specific url
    :return: html_list -> list of html (one item per page), num_pages -> number of pages
    """

    OFF_SET_P = 3
    WD_WAIT_s = 5
    num_pages = get_number_of_pages(url)
    html_list = []
    driver = webdriver.Chrome()
    if platform.system() == 'Linux':  # Linux system must specifically specify the path to chromedriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
    driver.get(url)
    if num_pages == 0:
        return html_list, num_pages

    div_num_next = str(num_pages + OFF_SET_P)
    xpath_next = "//*[@id=\"__next\"]/div/section/div/div[2]/div[1]/div[3]/div/div/div[" + div_num_next + "]/span"
    ex_script_scroll = "return arguments[0].scrollIntoView(true);"

    count = 0

    # this loop clicks through the flights by clicking on the next button
    # and collects all the flight specific links until reaching the last page
    while count < num_pages:
        count += 1
        try:
            driver.execute_script(ex_script_scroll, WebDriverWait(driver, WD_WAIT_s).until(EC.element_to_be_clickable((By.XPATH, xpath_next))))
            driver.find_element_by_xpath(xpath_next).click()
            html_list.append(driver.page_source)
        except TimeoutException:
            print("The page request timed-out...")
            break
        except WebDriverException:
            print("The WebDriver failed to scrape the page...")
            break

    return html_list, num_pages


def get_number_of_pages(url):
    """
    gets the number of pages on the airport departure website
    :param url: airport specific url
    :return: number_of_pages
    """

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    pagination = soup.select("span", class_="pagination__PageNavigation-s1515b5x-3 cKpakR")

    page_number_pagination = []
    for b in pagination:
        if b.get_text().isnumeric():
            page_number_pagination.append(b.get_text())
    if len(page_number_pagination) == 0:
        return 0
    number_of_pages = int(page_number_pagination[-1])
    return number_of_pages


def test_pagination(url):
    """checks if the length of the html list is equal to the number of pages per airport"""

    assert get_number_of_pages(url) == len(collect_flight_links(url))


def main():
    url= 'https://www.flightstats.com/v2/flight-tracker/departures/tlv'
    test_pagination(url)


if __name__ == "__main__":
    main()

