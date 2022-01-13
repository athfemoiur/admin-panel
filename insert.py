from time import sleep
from redis import Redis
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from divar_crawler import get_data
from decouple import config

from configs import STATE, CITY

client = Redis()
city_id, data = get_data()


def insert_districts(state_name, city_name, start):
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(3)
    driver.get(config('LOGIN_URL'))
    username = driver.find_element_by_xpath('/html/body/div/div[2]/div/form/div[1]/input')
    username.send_keys(config('MY_USERNAME'))
    password = driver.find_element_by_xpath('/html/body/div/div[2]/div/form/div[2]/input')
    password.send_keys(config('MY_PASSWORD'))
    submit = driver.find_element_by_xpath('/html/body/div/div[2]/div/form/div[3]/div[2]/button')
    submit.click()
    driver.get(config('DISTRICTS_URL'))
    btn = driver.find_element_by_xpath('//*[@id="fw-content"]/section[2]/div/div/div/div[1]/a[2]')
    btn.click()

    for index, d in enumerate(data[start::]):
        if index != 0 and index % 20 == 0:
            driver.refresh()
            btn = driver.find_element_by_xpath('//*[@id="fw-content"]/section[2]/div/div/div/div[1]/a[2]')
            btn.click()

        area = driver.find_element_by_xpath('//*[@id="distance_name"]')
        area.send_keys(d)

        state = Select(driver.find_element_by_xpath('//*[@id="state_id"]'))
        state.select_by_visible_text(state_name)
        city = Select(driver.find_element_by_xpath('//*[@id="city_id"]'))
        try:
            city.select_by_visible_text(city_name)
        except NoSuchElementException:
            if client.exists(f'start_{city_id}'):
                client.incr(f'start_{city_id}', index)
            else:
                client.set(f'start_{city_id}', index)

        save = driver.find_element_by_xpath('//*[@id="fw-content"]/section[2]/div/div/div/form/div[2]/button')
        save.click()
        sleep(1)
        refresh = driver.find_element_by_xpath('//*[@id="fw_refresh_btn"]')
        refresh.click()


def run():
    start = client.get(f'start_{city_id}')
    if start:
        insert_districts(STATE, CITY, int(start))
    else:
        insert_districts(STATE, CITY, 0)
