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


class Command(BaseCommand):
    help = 'Get Review From Page'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
    delay = 10

    def __init__(self):
        BaseCommand.__init__(self)
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--user-agent=' + self.user_agent)
        chrome_options.add_argument('--headless')
        self.spread_sheet = SpreadsheetData()
        self.browser = Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.browser, self.delay)
        self.actions = ActionChains(self.browser)

    @retry(TimeoutException, tries=3, delay=2)
    def get_review_volume(self, first_page):
        num = 0
        title = ""
        el_present = EC.presence_of_element_located((By.ID, 'taplc_location_reviews_list_responsive_detail_0'))
        self.wait.until(el_present)
        if first_page:
            number = self.browser.find_element_by_xpath(
                '//*[@id="taplc_location_reviews_list_responsive_detail_0"]/div/p/b[1]')
            num = int(number.text.replace(',', ''))
            title = self.browser.find_element_by_tag_name('h1').text
        print("Page is ready")
        return num, title

    def check_invisible_loading_shade(self):
        pass
        # shade_invisible = EC.invisibility_of_element_located(
        #     (By.CLASS_NAME, 'loadingShade'))
        # wait.until(shade_invisible)

    def press_more_content(self):
        try:
            more_content_buttons = self.browser.find_elements_by_css_selector('span.taLnk.ulBlueLinks')
            if more_content_buttons:
                for button in more_content_buttons:
                    if button.text == 'さらに表示':
                        invisible_loading_shade = EC.invisibility_of_element_located(
                            (By.XPATH, "//div[@class='loadingShade']")
                        )
                        self.wait.until(invisible_loading_shade)
                        button.click()
                        self.wait.until(invisible_loading_shade)
        except WebDriverException as e:
            print(e)

    def get_page_by_sel(self, url, first_page=False):
        print(url)
        self.browser.get(url)
        self.browser.implicitly_wait(3)
        num, title = self.get_review_volume(self.browser, first_page)
        first_page_info = (num, title)
        self.check_invisible_loading_shade()
        self.press_more_content()
        try:
            invisible_more_content = EC.invisibility_of_element_located(
                (By.XPATH, '//span[contains(text(), "さらに表示") and @class="taLnk ulBlueLinks"]'))
            self.wait.until(invisible_more_content)
        except TimeoutException:
            self.press_more_content()
        elements = self.browser.find_elements_by_css_selector('.review.hsx_review')
        reviews = []
        for element in elements:
            self.actions.move_to_element(element).perform()
            uid = element.find_element_by_xpath('//div[@class="memberOverlayLink"]').get_attribute('id')
            title = element.find_element_by_class_name('noQuotes').text
            content = element.find_element_by_class_name('partial_entry').text
            rating = element.find_element_by_class_name('ui_bubble_rating').get_attribute('class').split('_')[-1]
            reviews.append({"uid": uid, "title": title, "content": content, "rating": rating})
        return reviews, first_page_info

    @classmethod
    def make_list(cls, url, num, count=10):
        url_list = []
        for i in range(count, int(num / 10) * 10 + 10, 10):
            url_list.append(url.replace('.html', '-or{}.html'.format(i)))
        return url_list

    def record_reviews(self, spot, reviews):
        for review in reviews:
            r = Review.objects.get_or_create(uid=review['uid'], title=review['title'], content=review['content'], rating=int(review['rating']), spot=spot)[0]
            r.save()
        self.spread_sheet.update_count_cell_by_spot_id(spot.base_id, len(reviews))

    def record_first_page_info(self, spot_id, first_page_info):
        self.spread_sheet.record_first_page_info(spot_id, first_page_info)

    def check_reviews(self, spot_id):
        h = self.spread_sheet.find_by_spot_id(spot_id)
        count = h['count']
        if count == '':
            count = 0
        return int(count)

    def check_total_reviews(self, spot_id):
        h = self.spread_sheet.find_by_spot_id(spot_id)
        count = h['reviews']
        if count == '':
            count = 0
        return int(count)

    def spot_title(self, spot_id):
        h = self.spread_sheet.find_by_spot_id(spot_id)
        spot_name = h['spot_name']
        return spot_name

    def add_arguments(self, parser):
        parser.add_argument(
            '--spot-id', dest='spot-id', required=True,
            help='spot-id to get review',
        )

    def handle(self, *args, **options):
        spot_id = options['spot-id']
        spot_data = self.spread_sheet.find_by_spot_id(spot_id)
        url = spot_data['url']
        page = 1
        try:
            count = 10
            now_recorded_count = self.check_reviews(spot_id)

            if now_recorded_count == 0:
                page_reviews, first_page_info = self.get_page_by_sel(url, first_page=True)
                title = first_page_info[1]
                page_num = first_page_info[0]
                spot = Spot.objects.get_or_create(base_id=spot_id, title=title)[0]
                self.record_first_page_info(spot_id, first_page_info)
                self.record_reviews(spot, page_reviews)
            else:
                page_num = self.check_total_reviews(spot_id)
                count = now_recorded_count
                title = self.spot_title(spot_id)
            spot = Spot.objects.get_or_create(base_id=spot_id, title=title)[0]
            crawling_url_list = self.make_list(url, page_num, count)
            for url in crawling_url_list:
                time.sleep(1)
                page_reviews, first_page_info = self.get_page_by_sel(url)
                self.record_reviews(spot, page_reviews)
                page += 1
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(traceback.format_exception(exc_type, exc_obj, exc_tb))
            print(traceback.format_tb(e.__traceback__))
            print(e)
        finally:
            self.browser.close()

