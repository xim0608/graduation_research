from django.core.management.base import BaseCommand
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from review_based_recommender.models import City, CityAppend
from retry import retry
import sys
import os
import traceback
from selenium.webdriver.common.action_chains import ActionChains


class Command(BaseCommand):
    help = 'Get Cities From Cities List (Prefecture Top)'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
    delay = 10

    def __init__(self):
        BaseCommand.__init__(self)
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--user-agent=' + self.user_agent)
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1280,1024')
        self.browser = Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.browser, self.delay)
        self.actions = ActionChains(self.browser)
        self.pref_name = None

    def press_more_contents(self):
        has_more_contents = True
        while has_more_contents:
            try:
                more_content_button = self.browser.find_element_by_css_selector(
                    '.morePopularCities.ui_button.primary.chevron')
                print(more_content_button)
                if more_content_button:
                    self.browser.implicitly_wait(1.5)
                    more_content_button.click()
                    self.browser.implicitly_wait(1.5)
                else:
                    has_more_contents = False
            except WebDriverException as e:
                print(e)
                print("maybe no more content")
                has_more_contents = False

    def get_page_by_sel(self, url):
        print(url)
        self.browser.get(url)
        self.browser.implicitly_wait(1.5)
        city_ids = []
        cities = []

        ############
        # 都道府県ID
        ############
        h1 = self.browser.find_element_by_tag_name('h1').text
        self.pref_name = h1.split('の旅行情報')[0]
        print(self.pref_name)

        self.press_more_contents()
        self.browser.implicitly_wait(3)
        elements = self.browser.find_elements_by_xpath('//a[@class="popularCity hoverHighlight"]')
        print(elements)

        for element in elements:
            city = {}
            url = element.get_attribute('href')
            city_id = url.split('Tourism-')[1].split('-')[0]
            city_name = element.text.split('\n')[1]

            city['name'] = city_name
            city['id'] = city_id
            cities.append(city)
        return cities

    def add_arguments(self, parser):
        parser.add_argument(
            '--pref-id', dest='pref-id', required=True,
            help='pref-id to get review',
        )

    def handle(self, *args, **options):
        # saitama: g298175
        pref_id = options['pref-id']
        url = "https://tripadvisor.jp/Tourism-" + pref_id + ".html"
        # page = 1
        cities = []
        try:
            cities = self.get_page_by_sel(url=url)
            print(cities)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(traceback.format_exception(exc_type, exc_obj, exc_tb))
            print(traceback.format_tb(e.__traceback__))
            print(e)
        finally:
            self.browser.close()

        city_names = ''.join(list(map(lambda c: c.name, City.objects.filter(prefecture__name=self.pref_name))))
        for city in cities:
            print(city)
            c = None
            if not ('市' in city['name'] or '区' in city['name'] or '町' in city['name'] or '村' in city['name'])\
                    or not city['name'] in city_names:
                print('no name')
                continue
            elif city['name'] == '緑区' or city['name'] == '南区':
                c = City.objects.filter(name__contains=city['name'], prefecture__name=self.pref_name)
                c = c[0]
            elif '区' in city['name']:
                c = City.objects.get(name__contains=city['name'], prefecture__name=self.pref_name)
            else:
                # 神奈川には緑区が2つある
                c = City.objects.filter(name=city['name'], prefecture__name=self.pref_name)
                c = c[0]
            city_append = CityAppend.objects.get_or_create(city=c, ta_area_id=city['id'])
