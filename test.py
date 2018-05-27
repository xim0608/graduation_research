import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver import PhantomJS
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
delay = 3


def get_page_by_req(url):
    headers = {"User-Agent": user_agent}
    resp = requests.get(url, timeout=1, headers=headers)
    r_text = resp.text
    return r_text


def get_page_by_sel(browser, url, first_page=False):
    # options = FirefoxOptions()
    # options.add_argument("-headless")
    # browser = webdriver.Firefox()
    wait = WebDriverWait(browser, delay)
    num = 0
    browser.get(url)
    browser.implicitly_wait(3)
    try:
        el_present = EC.presence_of_element_located((By.ID, 'taplc_location_reviews_list_responsive_detail_0'))
        wait.until(el_present)
        if first_page:
            number = browser.find_element_by_xpath(
                '//*[@id="taplc_location_reviews_list_responsive_detail_0"]/div/p/b[1]')
            num = int(number.text.replace(',', ''))
        print("Page is ready")
    except TimeoutException:
        print("Loading took too much time")
    shade_invisible = EC.invisibility_of_element_located(
        (By.CLASS_NAME, 'loadingShade'))
    wait.until(shade_invisible)
    # try:
    #     el_present = EC.element_to_be_clickable((By.ID, 'taplc_location_review_keyword_search_modal_0_q'))
    #     wait.until(el_present)
    # except TimeoutException:
    #     print("review load failed")
    try:
        more_content_buttons = browser.find_elements_by_css_selector('span.taLnk.ulBlueLinks')
        # more_content_buttons = browser.find_elements_by_xpath('//span[contains(text(), "さらに表示")]')
        print(more_content_buttons)
        if more_content_buttons:
            for button in more_content_buttons:
                print(button.text)
                button.click()
    except StaleElementReferenceException:
        print("error")
    invisible_more_content = EC.invisibility_of_element_located(
        (By.XPATH, '//span[contains(text(), "さらに表示") and contains(@class, "taLnk")]'))
    wait.until(invisible_more_content)
    elements = browser.find_elements_by_css_selector('.review.hsx_review')

    for element in elements:
        print("title : {}".format(element.find_element_by_class_name('noQuotes').text))
        print("content: {}".format(element.find_element_by_class_name('partial_entry').text))
        rating = element.find_element_by_class_name('ui_bubble_rating').get_attribute('class').split('_')[-1]
        print("star: {}".format(rating))
    # browser.close()
    return num


def make_list(url, num):
    url_list = []
    for i in range(10, int(num / 10) * 10 + 10, 10):
        url_list.append(url.replace('.html', '-or{}.html'.format(i)))
    return url_list


if __name__ == '__main__':
    options = ChromeOptions()
    options.add_argument('--headless')
    # options.add_argument('--remote-debugging-port=9222')
    browser = Chrome(options=options)
    # num = 10
    # browser.implicitly_wait(1)
    url = 'https://www.tripadvisor.jp/Attraction_Review-g298173-d320009-Reviews-Minato_Mirai_21-Yokohama_Kanagawa_Prefecture_Kanto.html#REVIEWS'
    # # r_text = get_page_by_req(url)
    # # print(r_text)
    # # soup = BeautifulSoup(r_text, 'html.parser')
    # # soups = soup.find_all("div", class_="entry")
    # # for t in soups:
    # #     print(t.get_text())
    try:
        num = get_page_by_sel(browser, url, first_page=True)
        crawling_url_list = make_list(url, num)
        for url in crawling_url_list:
            time.sleep(1)
            get_page_by_sel(browser, url)
    finally:
        browser.close()
    # print(num)
    # num = 1326
