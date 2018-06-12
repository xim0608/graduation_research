from django.core.management.base import BaseCommand
from ...models import Spot, Review, SpreadsheetData, City
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException
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
        self.browser = Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.browser, self.delay)
        self.actions = ActionChains(self.browser)
        self.after_clawl_list = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--city-id', dest='city-id', required=True,
            help='city-id to get spots',
        )

    def get_page(self, url, first_page=False):
        self.browser.get(url)
        self.browser.implicitly_wait(1)
        elements = self.browser.find_elements_by_xpath('//*[@class="attraction_clarity_cell"]')
        spots = []
        last_page_num = 0
        if first_page:
            last_page_num = int(elements[0].find_element_by_xpath('//*[@class="pageNumbers"]/a[position()=last()]').text.replace(',', ''))
            #.split('観光スポット')[1].split('件')[0].replace(',', ''))
            print(last_page_num)
            title = self.browser.find_element_by_tag_name('h1').text
            self.city.title = title
            self.city.save()
        for element in elements:
            url = element.find_element_by_class_name('listing_title').find_element_by_tag_name('a').get_attribute('href')
            try:
                content = int(element.find_element_by_class_name('more').text.split('件')[0].replace(',', ''))
                print("url: {}, total_count: {}".format(url, content))
                spots.append({"url": url, "content": content})
            except NoSuchElementException:
                if 'Attractions' in url:
                    print('add crawling_list to {}'.format(url))
                    self.after_clawl_list.append(url)
                else:
                    print('no review page: {}'.format(url))

        if first_page:
            return last_page_num, spots
        else:
            return spots

    def get_after_crawl_page(self, url):
        self.browser.get(url)
        self.browser.implicitly_wait(1)
        elements = self.browser.find_elements_by_xpath('//*[@class="attraction_clarity_cell"]')
        spots = []
        num = 0
        for element in elements:
            url = element.find_element_by_class_name('listing_title').find_element_by_tag_name('a').get_attribute('href')
            try:
                content = int(element.find_element_by_class_name('more').text.split('件')[0].replace(',', ''))
                print("url: {}, total_count: {}".format(url, content))
                spots.append({"url": url, "content": content})
            except NoSuchElementException:
                if 'Attractions' in url:
                    print('add crawling_list to {}'.format(url))
                    self.after_clawl_list.append(url)
                else:
                    print('no review page: {}'.format(url))
        size = len(elements)
        return spots, size

    def save_spots(self, spots):
        for spot in spots:
            s = Spot.objects.get_or_create(url=spot['url'])[0]
            s.city = self.city
            s.save()

    def handle(self, *args, **options):
        city_id = options['city-id']
        self.city = City.objects.get(base_id=city_id)
        url = self.city.url
        print(url)
        try:
            last_page_num, spots = self.get_page(url, first_page=True)
            self.save_spots(spots)
            url_list = []
            for i in range(1, last_page_num):
                url_list.append(url.replace('.html', '-oa{}.html'.format(i * 30)))
            for url in url_list:
                spots = self.get_page(url)
                self.save_spots(spots)
            for url in self.after_clawl_list:
                print(url)
                spots, size = self.get_after_crawl_page(url)
                self.save_spots(spots)
                oa_count = 30
                while size == 30:
                    spots, size = self.get_after_crawl_page(url.replace('.html', '-oa{}.html'.format(oa_count)))
                    self.save_spots(spots)
                    if url == self.browser.current_url:
                        size = 0
                    oa_count += 30
            self.city.finish = True
            self.city.save()
        finally:
            self.browser.close()
