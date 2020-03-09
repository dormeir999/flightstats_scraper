"""This code clicks through all the pages"""

from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# options = Options()
# options.add_argument("start-maximized")
# options.add_argument("disable-infobars")
# options.add_argument("--disable-extensions")
# driver = webdriver.Chrome(chrome_options=options)
driver = webdriver.Chrome()
driver.get('https://www.flightstats.com/v2/flight-tracker/departures/zrh')



while True:
    try:
        driver.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"__next\"]/div/section/div/div[2]/div[1]/div[3]/div/div/div[16]/span"))))
        driver.find_element_by_xpath("//*[@id=\"__next\"]/div/section/div/div[2]/div[1]/div[3]/div/div/div[16]/span").click()

        #todo: get and parse html

        # htmprint("Navigating to Next Page")

    except (TimeoutException, WebDriverException) as e:
        # print("Last page reached")
        break