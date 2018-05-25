import requests
from bs4 import BeautifulSoup
from selenium import webdriver

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'


def get_page_by_req(url):
    headers = {"User-Agent": user_agent}
    resp = requests.get(url, timeout=1, headers=headers)
    r_text = resp.text
    return r_text

def get_page_by_sel(url):
    browser = webdriver.PhantomJS()
    browser.implicitly_wait(1)
    browser.get(url)
    e = browser.find_elements_by_css_selector('.review.hsx_review')
    print(len(e))






if __name__ == '__main__':
    url = 'https://www.tripadvisor.jp/Attraction_Review-g298173-d320009-Reviews-Minato_Mirai_21-Yokohama_Kanagawa_Prefecture_Kanto.html#REVIEWS'
    # r_text = get_page_by_req(url)
    # print(r_text)
    # soup = BeautifulSoup(r_text, 'html.parser')
    # soups = soup.find_all("div", class_="entry")
    # for t in soups:
    #     print(t.get_text())
    get_page_by_sel(url)