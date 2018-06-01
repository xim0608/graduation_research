from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException
import time
from retry import retry
from ...models import Spot, Review, SpreadsheetData
import sys
import os
import traceback
from selenium.webdriver.common.action_chains import ActionChains
from optparse import make_option

class Command(BaseCommand):
    help = 'Get Review From Page'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
    delay = 10

    # def add_arguments(self, parser):

    @retry(TimeoutException, tries=3, delay=2)
    def get_review_volume(self, browser, wait, first_page):
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

    def check_invisible_loading_shade(self, wait):
        pass
        # shade_invisible = EC.invisibility_of_element_located(
        #     (By.CLASS_NAME, 'loadingShade'))
        # wait.until(shade_invisible)

    def press_more_content(self, browser, wait):
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

    def get_page_by_sel(self, browser, url, first_page=False):
        print(url)
        wait = WebDriverWait(browser, self.delay)
        browser.get(url)
        browser.implicitly_wait(3)
        num, title = self.get_review_volume(browser, wait, first_page)
        first_page_info = (num, title)
        self.check_invisible_loading_shade(wait)
        self.press_more_content(browser, wait)
        try:
            invisible_more_content = EC.invisibility_of_element_located(
                (By.XPATH, '//span[contains(text(), "さらに表示") and @class="taLnk ulBlueLinks"]'))
            wait.until(invisible_more_content)
        except TimeoutException:
            self.press_more_content(browser, wait)
        actions = ActionChains(browser)
        elements = browser.find_elements_by_css_selector('.review.hsx_review')
        reviews = []
        for element in elements:
            actions.move_to_element(element).perform()
            uid = element.find_element_by_xpath('//div[@class="memberOverlayLink"]').get_attribute('id')
            title = element.find_element_by_class_name('noQuotes').text
            content = element.find_element_by_class_name('partial_entry').text
            rating = element.find_element_by_class_name('ui_bubble_rating').get_attribute('class').split('_')[-1]
            # print("uid : {}".format(uid))
            # print("title : {}".format(title))
            # print("content: {}".format(content))
            # print("rating: {}".format(rating))
            reviews.append({"uid": uid, "title": title, "content": content, "rating": rating})
        return reviews, first_page_info

    def make_list(self, url, num, count=10):
        url_list = []
        for i in range(count, int(num / 10) * 10 + 10, 10):
            url_list.append(url.replace('.html', '-or{}.html'.format(i)))
        return url_list

    def record_reviews(self, spreadsheet, spot, reviews):
        # TODO: レビューの数を現在のスプレッドシートの数と足し合わせる
        print(reviews)
        for review in reviews:
            r = Review.objects.get_or_create(uid=review['uid'], title=review['title'], content=review['content'], rating=int(review['rating']), spot=spot)[0]
            r.save()
        spreadsheet.update_count_cell_by_spot_id(spot.base_id, len(reviews))

    def record_first_page_info(self, spreadsheet, spot_id, first_page_info):
        spreadsheet.record_first_page_info(spot_id, first_page_info)

    def check_reviews(self, spreadsheet, spot_id):
        h = spreadsheet.find_by_spot_id(spot_id)
        count = h['count']
        if count == '':
            count = 0
        return int(count)

    def check_total_reviews(self, spreadsheet, spot_id):
        h = spreadsheet.find_by_spot_id(spot_id)
        count = h['reviews']
        if count == '':
            count = 0
        return int(count)

    def spot_title(self, spreadsheet, spot_id):
        h = spreadsheet.find_by_spot_id(spot_id)
        spot_name = h['spot_name']
        return spot_name

    def add_arguments(self, parser):
        parser.add_argument(
            '--spot-id', dest='spot-id', required=True,
            help='spot-id to get review',
        )

    def handle(self, *args, **options):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--user-agent=' + self.user_agent)
        chrome_options.add_argument('--headless')
        spread_sheet = SpreadsheetData()
        browser = Chrome(options=chrome_options)
        spot_id = options['spot-id']
        spot_data = spread_sheet.find_by_spot_id(spot_id)
        url = spot_data['url']
        # url = 'https://www.tripadvisor.jp/Attraction_Review-g298173-d320009-Reviews-Minato_Mirai_21-Yokohama_Kanagawa_Prefecture_Kanto.html#REVIEWS'
        # base_id = url.split('Attraction_Review-')[1].split('-Reviews')[0]
        # print(base_id)
        page = 1
        try:
            count = 10
            now_recorded_count = self.check_reviews(spread_sheet, spot_id)

            if now_recorded_count == 0:
                page_reviews, first_page_info = self.get_page_by_sel(browser, url, first_page=True)
                title = first_page_info[1]
                page_num = first_page_info[0]
                spot = Spot.objects.get_or_create(base_id=spot_id, title=title)[0]
                self.record_first_page_info(spread_sheet, spot_id, first_page_info)
                self.record_reviews(spread_sheet, spot, page_reviews)
            else:
                page_num = self.check_total_reviews(spread_sheet, spot_id)
                count = now_recorded_count
                title = self.spot_title(spread_sheet, spot_id)
            spot = Spot.objects.get_or_create(base_id=spot_id, title=title)[0]
            crawling_url_list = self.make_list(url, page_num, count)
            for url in crawling_url_list:
                time.sleep(1)
                page_reviews, first_page_info = self.get_page_by_sel(browser, url)
                self.record_reviews(spread_sheet, spot, page_reviews)
                # print(page_reviews)
                page += 1
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(traceback.format_exception(exc_type, exc_obj, exc_tb))
            print(traceback.format_tb(e.__traceback__))
            print(e)
        finally:
            browser.close()
            # print(reviews)

