from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException
import time
from retry import retry

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
delay = 10


@retry(TimeoutException, tries=3, delay=2)
def get_review_volume(browser, wait, first_page):
    num = 0
    title = ""
    el_present = EC.presence_of_element_located((By.ID, 'taplc_location_reviews_list_responsive_detail_0'))
    wait.until(el_present)
    if first_page:
        number = browser.find_element_by_xpath(
            '//*[@id="taplc_location_reviews_list_responsive_detail_0"]/div/p/b[1]')
        num = int(number.text.replace(',', ''))
        title = browser.find_element_by_tag_name('h1').text
    print("Page is ready")
    return num, title


def check_invisible_loading_shade(wait):
    pass
    # shade_invisible = EC.invisibility_of_element_located(
    #     (By.CLASS_NAME, 'loadingShade'))
    # wait.until(shade_invisible)


def press_more_content(browser, wait):
    try:
        more_content_buttons = browser.find_elements_by_css_selector('span.taLnk.ulBlueLinks')
        # more_content_buttons = browser.find_elements_by_xpath('//span[contains(text(), "さらに表示")]')
        # print(more_content_buttons)
        if more_content_buttons:
            for button in more_content_buttons:
                if button.text == 'さらに表示':
                    invisible_loading_shade = EC.invisibility_of_element_located(
                        (By.XPATH, "//div[@class='loadingShade']")
                    )
                    wait.until(invisible_loading_shade)
                    button.click()
                    wait.until(invisible_loading_shade)
    except WebDriverException as e:
        print(e)
        # check_invisible_loading_shade(wait)


def get_page_by_sel(browser, url, first_page=False):
    print(url)
    wait = WebDriverWait(browser, delay)
    browser.get(url)
    browser.implicitly_wait(3)
    num, title = get_review_volume(browser, wait, first_page)
    first_page_info = (num, title)
    check_invisible_loading_shade(wait)
    press_more_content(browser, wait)
    try:
        invisible_more_content = EC.invisibility_of_element_located(
            (By.XPATH, '//span[contains(text(), "さらに表示") and @class="taLnk ulBlueLinks"]'))
        wait.until(invisible_more_content)
    except TimeoutException:
        press_more_content(browser, wait)

    elements = browser.find_elements_by_css_selector('.review.hsx_review')
    reviews = []
    for element in elements:
        uid = element.find_element_by_class_name('memberOverlayLink').get_attribute('id')
        title = element.find_element_by_class_name('noQuotes').text
        content = element.find_element_by_class_name('partial_entry').text
        rating = element.find_element_by_class_name('ui_bubble_rating').get_attribute('class').split('_')[-1]
        # print("uid : {}".format(uid))
        # print("title : {}".format(title))
        # print("content: {}".format(content))
        # print("rating: {}".format(rating))
        reviews.append({"uid": uid, "title": title, "content": content, "rating": rating})
    return reviews, first_page_info


def make_list(url, num):
    url_list = []
    for i in range(10, int(num / 10) * 10 + 10, 10):
        url_list.append(url.replace('.html', '-or{}.html'.format(i)))
    return url_list


if __name__ == '__main__':
    options = ChromeOptions()
    options.add_argument('--user-agent=' + user_agent)
    options.add_argument('--headless')
    browser = Chrome(options=options)
    url = 'https://www.tripadvisor.jp/Attraction_Review-g298173-d320009-Reviews-Minato_Mirai_21-Yokohama_Kanagawa_Prefecture_Kanto.html#REVIEWS'
    base_id = url.split('Attraction_Review-')[1].split('-Reviews')[0]
    print(base_id)
    page = 1
    reviews = []
    try:
        page_reviews, first_page_info = get_page_by_sel(browser, url, first_page=True)
        crawling_url_list = make_list(url, first_page_info[0])
        title = first_page_info[1]
        print(title)
        reviews.append(page_reviews)
        for url in crawling_url_list:
            time.sleep(1)
            page_reviews, first_page_info = get_page_by_sel(browser, url)
            reviews.append(page_reviews)
            print(page_reviews)
            page += 1
    except Exception as e:
        print(e)
        print(page)
    finally:
        browser.close()
        print(reviews)
