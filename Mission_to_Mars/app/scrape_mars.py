from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime as dt
import time


def scrape_all():

    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store in dictionary.
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "hemispheres": hemispheres(browser),
        "weather": twitter_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    html = browser.html
    soup = bs(html, 'html.parser')

    slide = soup.find('li', class_='slide')

    news_title = slide.find("div", class_='content_title').text
    news_p = slide.find("div", class_='article_teaser_body').text

    return news_title, news_p


def featured_image(browser):

    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    browser.visit(url)
    html = browser.html
    soup = bs(html, 'html.parser')

    s = soup.find('article', class_='carousel_item')['style']
    img_url = 'https://www.jpl.nasa.gov' + \
        s[(s.find("('") + len("('")): s.find("')")]

    return img_url


def hemispheres(browser):

    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(url)
    browser.is_element_present_by_css("div.description", wait_time=3)

    html = browser.html
    soup = bs(html, 'html.parser')

    links = soup.find_all('a', class_='itemLink product-item')

    link_list = []

    for link in links:
        link_list.append(link.get('href'))

    link_list = list(set(link_list))


    def contains_word(t):
        return t and 'Sample' in t


    hemisphere_image_urls = []

    for link in link_list:

        browser.visit('https://astrogeology.usgs.gov/' + link)
        browser.is_element_present_by_css("div.ul.li", wait_time=1)

        html = browser.html
        soup = bs(html, 'html.parser')
        link = soup.find('a', text=contains_word)

        title = soup.head.title.text
        title = title[0:title.find(" |")]

        Dict = {"title": title, "img_url": link.get('href')}
        hemisphere_image_urls.append(Dict)

    return hemisphere_image_urls


def twitter_weather(browser):

    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    browser.is_element_present_by_css("div.aria-label", wait_time=3)

    html = browser.html
    soup = bs(html, 'html.parser')

    main = soup.find('main')

    def contains_word(t):
        return t and 'InSight sol' in t

    mars_weather = main.find('span', text=contains_word).text

    return mars_weather



def mars_facts():
    try:
        df = pd.read_html("http://space-facts.com/mars/")[0]
    except BaseException:
        return None

    df.columns = ["description", "value"]
    df.set_index("description", inplace=True)

    # Add some bootstrap styling to <table>
    return df.to_html(classes="table table-striped")


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())