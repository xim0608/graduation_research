from locations.models import City, CityAppend, Prefecture, PrefectureAppend
from review_based_recommender.models import Spot, Review
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
import json
import os
import traceback
import slackweb
from socket import gethostname


ta_slack = slackweb.Slack(url=os.environ.get('SLACK_WEBHOOK_URL'))
ta_spot_slack = slackweb.Slack(url=os.environ.get('SLACK_WEBHOOK_URL_2'))



class PrefPage:
    help = 'Get Cities From Cities List (Prefecture Top)'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
    delay = 10

    def __init__(self, pref_base_id):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--user-agent=' + self.user_agent)
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1280,1024')
        self.browser = Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.browser, self.delay)
        self.actions = ActionChains(self.browser)
        self.pref_base_id = pref_base_id
        self.prefecture = None

    def press_more_contents(self):
        has_more_contents = True
        while has_more_contents:
            try:
                more_content_button = self.browser.find_element_by_css_selector(
                    '.morePopularCities.ui_button.primary.chevron')
                # print(more_content_button)
                if more_content_button:
                    self.browser.implicitly_wait(3)
                    more_content_button.click()
                    self.browser.implicitly_wait(3)
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
        cities = []

        ############
        # 都道府県ID
        ############
        h1 = self.browser.find_element_by_tag_name('h1').text

        pref_name = h1.split('の旅行情報')[0]
        self.prefecture = Prefecture.objects.get(name=pref_name)
        PrefectureAppend.objects.get_or_create(prefecture=self.prefecture, base_id=self.pref_base_id)

        self.press_more_contents()
        self.browser.implicitly_wait(3)
        elements = self.browser.find_elements_by_xpath('//a[@class="popularCity hoverHighlight"]')
        # print(elements)

        for element in elements:
            city = {}
            url = element.get_attribute('href')
            city_id = url.split('Tourism-')[1].split('-')[0]
            city_name = element.text.split('\n')[1]

            city['name'] = city_name
            city['id'] = city_id
            cities.append(city)
        return cities

    def add_check_city_name(self, name):
        # 鎌ヶ谷, 鎌ケ谷..etc
        if 'ヶ' in name:
            return name + self.toggle_ga(name)
        elif 'ケ' in name:
            return name + self.toggle_ga(name)
        else:
            return name

    def toggle_ga(self, name):
        if 'ヶ' in name:
            return name.replace('ヶ', 'ケ')
        elif 'ケ' in name:
            return name.replace('ケ', 'ヶ')

    def get(self):
        # saitama: g298175
        pref_id = self.pref_base_id
        url = "https://tripadvisor.jp/Tourism-" + pref_id + ".html"
        # page = 1
        cities = []
        try:
            cities = self.get_page_by_sel(url=url)
            # print(cities)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(traceback.format_exception(exc_type, exc_obj, exc_tb))
            print(traceback.format_tb(e.__traceback__))
            print(e)
        finally:
            self.browser.close()
        cities_name_list = list(
            map(lambda c: self.add_check_city_name(c.name), City.objects.filter(prefecture=self.prefecture)))

        city_names = ''.join(cities_name_list)
        for city in cities:
            print(city)
            c = None
            if not ('市' in city['name'] or '区' in city['name'] or '町' in city['name'] or '村' in city['name']) \
                    or not city['name'] in city_names:
                print('no name')
                continue
            elif (self.prefecture.name == '大阪府') and ('区' in city['name']):
                c = City.objects.filter(name__contains='大阪市' + city['name'], prefecture=self.prefecture)
                c = c[0]
            elif (self.prefecture.name == '兵庫県') and ('区' in city['name']):
                c = City.objects.filter(name__contains='神戸市' + city['name'], prefecture=self.prefecture)
                c = c[0]
            elif (self.prefecture.name == '兵庫県') and ('区' in city['name']):
                c = City.objects.filter(name__contains='神戸市' + city['name'], prefecture=self.prefecture)
                c = c[0]
            elif (self.prefecture.name == '福岡県') and ('東区' == city['name']):
                c = City.objects.filter(name__contains='福岡市' + city['name'], prefecture=self.prefecture)
                c = c[0]
            elif city['name'] == '緑区' or city['name'] == '南区':
                c = City.objects.filter(name__contains=city['name'], prefecture=self.prefecture)
                c = c[0]
            elif '区' in city['name']:
                c = City.objects.get(name__contains=city['name'], prefecture=self.prefecture)
            else:
                # 神奈川には緑区が2つある
                c = City.objects.filter(name=city['name'], prefecture=self.prefecture)
                if len(c) < 1:
                    c = City.objects.filter(name=self.toggle_ga(city['name']), prefecture=self.prefecture)
                c = c[0]
            city_append = CityAppend.objects.get_or_create(city=c, ta_area_id=city['id'])
        print('finished')


class CityPage:
    help = 'Get Review From Page'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
    delay = 10

    def __init__(self, city_base_id):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--user-agent=' + self.user_agent)
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1280,1024')
        self.browser = Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.browser, self.delay)
        self.actions = ActionChains(self.browser)
        self.city = City.objects.get(cityappend__ta_area_id=city_base_id)
        self.after_clawl_list = []
        self.counter = 0

    def get_page(self, url, first_page=False):
        self.browser.get(url + '?geobroaden=false')
        self.browser.implicitly_wait(3)

        elements = self.browser.find_elements_by_xpath('//*[@class="attraction_clarity_cell"]')
        spots = []
        last_page_num = 0
        if len(elements) == 0:
            print('no spots in this area')
            return last_page_num, []
        if first_page:
            last_page_number = elements[0].find_elements_by_xpath('//*[@class="pageNumbers"]/a[position()=last()]')
            if len(last_page_number) > 0:
                last_page_num = int(last_page_number[0].text.replace(',', ''))
            else:
                last_page_num = 1
            print("This city has {} pages.".format(last_page_num))
        for element in elements:
            url = element.find_element_by_class_name('listing_title').find_element_by_tag_name('a').get_attribute(
                'href')
            try:
                total_count = int(element.find_element_by_class_name('more').text.split('件')[0].replace(',', ''))
                print("url: {}, total_count: {}".format(url, total_count))
                spots.append({"url": url, "total_count": total_count})
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
        self.browser.get(url + '?geobroaden=false')
        self.browser.implicitly_wait(1)
        elements = self.browser.find_elements_by_xpath('//*[@class="attraction_clarity_cell"]')
        spots = []
        num = 0
        for element in elements:
            url = element.find_element_by_class_name('listing_title').find_element_by_tag_name('a').get_attribute(
                'href')
            if url is None:
                continue
            try:
                total_count = int(element.find_element_by_class_name('more').text.split('件')[0].replace(',', ''))
                print("url: {}, total_count: {}".format(url, total_count))
                spots.append({"url": url, "total_count": total_count})
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
            area_id = spot['url'].split('Attraction_Review-')[1].split('-')[0]
            # urlに含まれるarea_idがcitiesのta_area_idと等しい、
            # もしくはurlに含まれるarea_idがcitiesのta_area_idに存在しない場合(東京都とか関東とか)
            if self.city.cityappend.ta_area_id == area_id or \
                    City.objects.filter(prefecture__city__id=self.city.id, cityappend__ta_area_id=area_id).count() < 1:
                s = Spot.objects.get_or_create(url=spot['url'])[0]
                if s.all_lang_total_count is not None and s.all_lang_total_count != spot['total_count']:
                    s.is_updatable = True
                s.all_lang_total_count = spot['total_count']
                s.city = self.city
                s.save()
                self.counter += 1

    def get(self):
        base_url = self.city.url
        print(base_url)
        try:
            last_page_num, spots = self.get_page(base_url, first_page=True)
            if last_page_num == 0 and spots == []:
                self.city.cityappend.finish = True
                self.city.cityappend.save()
                print('no spots in {}'.format(self.city.name))
                raise Exception
            url = self.browser.current_url
            self.save_spots(spots)
            url_list = []
            for i in range(1, last_page_num):
                url_list.append(url.replace('.html', '-oa{}.html?geobroaden=false'.format(i * 30)))
            for url in url_list:
                spots = self.get_page(url)
                self.save_spots(spots)
            for url in self.after_clawl_list:
                print(url)
                spots, size = self.get_after_crawl_page(url)
                self.save_spots(spots)
                oa_count = 30
                while size == 30:
                    spots, size = self.get_after_crawl_page(
                        url.replace('.html', '-oa{}.html?geobroaden=false'.format(oa_count)))
                    self.save_spots(spots)
                    if url == self.browser.current_url:
                        size = 0
                    oa_count += 30
            self.city.cityappend.finish = True
            self.city.cityappend.save()
        finally:
            self.browser.close()
            ta_slack.notify(text="finish city :{}, count: {}, host: {}".format(self.city.name, self.city.spot_set.count(), gethostname()))
        print(self.counter)


class SpotPage:
    help = 'Get Review From Page'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
    delay = 10

    def __init__(self, spot_base_id):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--user-agent=' + self.user_agent)
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1280,1024')
        self.delay = 10
        self.browser = Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.browser, self.delay)
        self.actions = ActionChains(self.browser)
        self.spot = Spot.objects.get(base_id=spot_base_id)

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

            # set location
            # import pdb;pdb.set_trace()
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//div/script[@type='application/ld+json']")))
            breadcrumb_json = self.browser.find_element_by_xpath("//div/script[@type='application/ld+json']")\
                .get_attribute('innerHTML')
            if breadcrumb_json:
                breadcrumb = json.loads(breadcrumb_json)
                for list_item in reversed(breadcrumb['itemListElement']):
                    ta_area_id = list_item["@id"].split('-')[1].split('-')[0]
                    c = City.objects.filter(cityappend__ta_area_id=ta_area_id)
                    if len(c) > 0:
                        print(c[0])
                        self.spot.city = c[0]
                        self.spot.valid_area = True
                        self.spot.save()
                        break
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
        update_counter = 0
        for review in reviews:
            r_s = Review.objects.filter(username=review['uid'], title=review['title'], content=review['content'],
                                        rating=int(review['rating']), spot=self.spot)
            if len(r_s) < 1:
                r = Review.objects.create(username=review['uid'], title=review['title'], content=review['content'],
                                          rating=int(review['rating']), spot=self.spot)
                update_counter += 1

        self.spot.update_count(count=update_counter)

    def get(self):
        print(self.spot)
        url = self.spot.url
        page = 1
        try:
            count = 10
            now_recorded_count = self.spot.count
            print(now_recorded_count)
            page_reviews, first_page_info = self.get_page_by_sel(url, first_page=True)
            title = first_page_info[1]
            reviews_count = first_page_info[0]
            self.spot.title = title
            self.spot.total_count = reviews_count
            self.spot.save()

            if now_recorded_count == 0:
                self.record_reviews(page_reviews)
            else:
                reviews_count = self.spot.total_count
                count = now_recorded_count
            crawling_url_list = self.make_list(url, reviews_count, count)
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
            self.spot.count = self.spot.review_set.count()
            ta_spot_slack.notify(text="finish spot :{}, count: {}, host: {}".format(self.spot.name, self.spot.count, gethostname()))
