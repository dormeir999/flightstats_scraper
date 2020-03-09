from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0

url = 'https://www.flightstats.com/v2/flight-tracker/departures/zrh'

driver = webdriver.Chrome()
driver.get(url)
wait = WebDriverWait(driver, 100)
html = driver.page_source
print(html)


