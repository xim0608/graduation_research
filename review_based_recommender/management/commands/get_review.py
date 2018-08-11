from django.core.management.base import BaseCommand
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from retry import retry
from ...models import Spot, Review, ZipCode, City
import sys
import os
import traceback
import json
from selenium.webdriver.common.action_chains import ActionChains
import time


class Command(BaseCommand):
    help = 'Get Review From Page'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
    delay = 10

    def __init__(self):
        BaseCommand.__init__(self)
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--user-agent=' + self.user_agent)
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1280,1024')
        self.delay = 10
        self.browser = Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.browser, self.delay)
        self.actions = ActionChains(self.browser)
        self.spot = None

    # @retry((TimeoutException, NoSuchElementException), tries=3, delay=2)
    def get_review_volume(self, first_page):
        print('try to get review volume')
        num = 0
        title = ""
        el_present = EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="REVIEWS"]'))
        self.wait.until(el_present)

        if first_page:
            title = self.browser.find_element_by_tag_name('h1').text
            retry_count = 5
            for i in range(retry_count):
                less_than_10 = []
                more_than_10 = self.browser.find_elements_by_xpath(
                    '//*[@id="taplc_location_reviews_list_responsive_detail_0"]/div/p/b[1]')
                if len(more_than_10) == 0:
                    less_than_10 = self.browser.find_elements_by_xpath(
                        '//label[@for="taplc_location_review_filter_controls_responsive_0_filterLang_ja"]/span')
                if len(less_than_10) == 0:
                    less_than_10.extend(self.browser.find_elements_by_xpath(
                        '//label[@for="filters_detail_language_filterLang_ja"]/span'))
                if len(less_than_10) == 0:
                    # check only english review
                    header_counts = self.browser.find_elements_by_xpath(
                        '//*[@id="REVIEWS"]//span[@class="reviews_header_count"]')
                    en_counts = self.browser.find_elements_by_xpath(
                        '//label[@for="filters_detail_language_filterLang_en"]/span')
                    ja = self.browser.find_elements_by_xpath('//label[@for="filters_detail_language_filterLang_ja"]')
                    if len(header_counts) > 0 and len(en_counts) > 0 and len(ja) > 0:
                        header_count = int(header_counts[0].text.replace('(', '').replace(')', '').replace(',', ''))
                        en_count = int(en_counts[0].text.replace('(', '').replace(')', '').replace(',', ''))
                        if header_count == en_count and ja[0].text == '日本語':
                            num = 0
                            break
                if len(more_than_10) > 0:
                    # more than 10 reviews page
                    number = more_than_10[0]
                    num = int(number.text.replace(',', ''))
                    break
                elif len(less_than_10) > 0:
                    # less than 10 reviews page
                    number = less_than_10[0]
                    num = int(number.text.replace('(', '').replace(')', '').replace(',', ''))
                    break
                elif i + 1 == retry_count:
                    print('failed to get review volume')
                    raise TimeoutException
                else:
                    # TODO: add new page type notification to slack
                    print('try again...')
                    self.browser.refresh()
                    self.browser.implicitly_wait(3)
                    el_present = EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="REVIEWS"]'))
                    self.wait.until(el_present)
        print("{} Page is ready. japanese review: {}".format(title, num))
        return num, title

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

    def check_popup(self):
        l = self.browser.find_elements_by_xpath('//*[@id="taplc_slide_up_messaging_0"]/div')
        if len(l) > 0:
            self.browser.find_element_by_xpath('//*[@id="taplc_slide_up_messaging_0"]/div/span').click()

    def get_page_by_sel(self, url, first_page=False):
        print(url)
        self.browser.get(url)

        self.check_popup()
        num, title = self.get_review_volume(first_page)
        first_page_info = (num, title)
        self.press_more_content()
        try:
            invisible_more_content = EC.invisibility_of_element_located(
                (By.XPATH, '//span[contains(text(), "さらに表示") and @class="taLnk ulBlueLinks"]'))
            self.wait.until(invisible_more_content)
        except TimeoutException:
            print("timeout line 80")
            self.press_more_content()
        elements = self.browser.find_elements_by_class_name('review-container')
        reviews = []
        for element in elements:
            try:
                invisible_more_content = EC.invisibility_of_element_located(
                    (By.XPATH, '//span[contains(text(), "さらに表示") and @class="taLnk ulBlueLinks"]'))
                self.wait.until(invisible_more_content)
            except TimeoutException:
                print("timeout line 94")
                self.press_more_content()

            uids = element.find_elements_by_xpath('.//div[@class="username mo"]')
            if len(uids) > 0:
                uid = uids[0].text
            else:
                uid = element.find_element_by_xpath('.//div[@class="info_text"]/div').text
            title = element.find_element_by_class_name('noQuotes').text
            content = element.find_element_by_class_name('partial_entry').text
            rating = element.find_element_by_class_name('ui_bubble_rating').get_attribute('class').split('_')[-1]
            reviews.append({"uid": uid, "title": title, "content": content, "rating": rating})
        return reviews, first_page_info

    @classmethod
    def make_list(cls, url, num, count=10):
        url_list = []
        for i in range(int(count/10)*10, int(num / 10) * 10 + 10, 10):
            url_list.append(url.replace('.html', '-or{}.html'.format(i)))
        return url_list

    def record_reviews(self, reviews):
        for review in reviews:
            r = Review.objects.get_or_create(username=review['uid'], title=review['title'], content=review['content'],
                                             rating=int(review['rating']), spot=self.spot)[0]
            r.save()
        self.spot.update_count(count=len(reviews))

    def record_first_page_info(self, title, page_num):
        self.spot.title = title
        self.spot.total_count = page_num
        self.spot.save()

    def add_arguments(self, parser):
        parser.add_argument(
            '--spot-id', dest='spot-id', required=True,
            help='spot-id to get review',
        )

    def handle(self, *args, **options):
        spot_id = options['spot-id']
        self.spot = Spot.objects.get(base_id=spot_id)
        print(self.spot)
        url = self.spot.url
        page = 1
        try:
            count = 10
            now_recorded_count = self.spot.count
            print(now_recorded_count)
            if now_recorded_count == 0:
                page_reviews, first_page_info = self.get_page_by_sel(url, first_page=True)
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//div/script[@type='application/ld+json']")))
                breadcrumb_json = self.browser.find_element_by_xpath("//div/script[@type='application/ld+json']") \
                    .get_attribute('innerHTML')
                if breadcrumb_json:
                    breadcrumb = json.loads(breadcrumb_json)
                    for list_item in reversed(breadcrumb['itemListElement']):
                        ta_area_id = list_item["@id"].split('-')[1].split('-')[0]
                        c = City.objects.filter(cityappend__ta_area_id=ta_area_id)
                        if len(c) > 0:
                            self.spot.city = c[0]
                            self.spot.save()
                            break
                title = first_page_info[1]
                page_num = first_page_info[0]
                self.record_first_page_info(title, page_num)
                self.record_reviews(page_reviews)
            else:
                page_num = self.spot.total_count
                count = now_recorded_count
            crawling_url_list = self.make_list(url, page_num, count)
            for url in crawling_url_list:
                page_reviews, first_page_info = self.get_page_by_sel(url)
                self.record_reviews(page_reviews)
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
