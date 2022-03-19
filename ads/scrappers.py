import requests
from bs4 import BeautifulSoup
from ads.models import MainCategory, SubCategory, Advertisement
import re
import time


class HomeScrapper():
    """
    Handles the behavior of scrapping the site home page
    the categories attribute is a list of tuples with three elements:
    (main category name, list of subcategories, url name)
    """

    def __init__(self):
        self.url = 'http://www.anuncioneon.es/'
        self.categories = self.get_categories_data()

    def get_page_content(self):
        """ Sends a GET request to the site homepage and returns the page content """
        response = requests.get(self.url)
        if response.ok:
            return response.text
        else:
            return None

    def get_soup(self):
        """ Return the soup object from page content """
        content = self.get_page_content()
        soup = BeautifulSoup(content, 'html.parser')
        return soup

    def get_category_divs(self):
        """ Returns the div blocks that contains all main categories and subcategories """
        soup = self.get_soup()
        return soup.find_all('div', id='seccion')

    def get_categories_data(self):
        """
        Initialize the self.category dict attribute
        each key is a main category with a list of 
        their respective subcategories as values
        """
        categories = []
        for category_div in self.get_category_divs():
            main_category = self.get_main_category(category_div)
            subcategories = self.get_sub_categories(category_div)
            url_name = self.get_url_name(category_div)
            categories.append((main_category, subcategories, url_name))
        return categories

    def get_main_category(self, category_div):
        """ Returns the main category from a given category block """
        return category_div.find('div', style='margin:0px; ').text

    def get_sub_categories(self, category_div):
        """ Returns a list of all subcategories given a category block """
        subcategories = []
        subcategories_soup = category_div.find_all('a', style="font-size:8pt;text-decoration:none;")
        for subcategory in subcategories_soup:
            subcategories.append(subcategory.text)
        return subcategories

    def get_url_name(self, category_div):
        """ Get the url name of the given category """
        a_tag = category_div.find('a', style="font-size:9pt;font-weight:bold;")
        url_name = re.search(r'.+/anunciosgratis/(.+)/"', str(a_tag)).group(1)
        return url_name

    def store_categories(self):
        """ Store all main categories and their subcategories in the database """
        MainCategory.objects.all().delete()
        SubCategory.objects.all().delete()

        for main_category, subcategories, url_name in self.categories:
            main_category = MainCategory.objects.create(category=main_category, url_name=url_name)
            for subcategory in subcategories:
                SubCategory.objects.create(main_category=main_category, subcategory=subcategory)


class AdScrapper():
    """ Scrappes the ads in the first page of each Ad category page """
    
    def __init__(self):
        self.url_names = self.get_url_names()
        self.base_url = 'http://www.anuncioneon.es/anunciosgratis/'
        self.ads = self.get_all_ads()

    def get_url_names(self):
        """ 
        Initializes url_names class attribute by getting every url_name from MainCategory model 
        """
        url_names = []
        for category in MainCategory.objects.all():
            url_names.append(category.url_name)
        return url_names

    def get_page_content(self, url_name):
        """ Returns the html page content of the category """
        full_url = self.base_url + url_name
        response = requests.get(full_url)
        return response.text

    def get_soup(self, url_name):
        """ Returns soup object of the category page """
        content = self.get_page_content(url_name)
        soup = BeautifulSoup(content, 'lxml')
        return soup

    def get_category_ads(self, url_name):
        """ Get at most the first 20 ads from the category page """
        soup = self.get_soup(url_name)
        ads = soup.find_all('li', class_='item')
        return ads
        # if len(ads) > 20:
        #     return ads[:20]
        # else:
        #     return ads

    def get_ad_title(self, ad_soup):
        """ Returns the title of the Ad given its soup object """
        styles = "cursor:pointer;font-size: 15px;color:#00c;word-wrap: break-word;text-decoration:underline;"
        title_soup = ad_soup.find('span', style=styles)
        if title_soup:
            return title_soup.text
        else:
            return ''

    def get_ad_subtitle(self, ad_soup):
        """ Returns the subtitle of the Ad given its soup object """
        subtitle_soup = ad_soup.find('i')
        if subtitle_soup:
            return subtitle_soup.text
        else:
            return ''

    def get_ad_price(self, ad_soup):
        """ Returns the price of the ad """
        price_soup = ad_soup.find('b')
        price = 0
        if price_soup:
            try:
                price = int(price_soup.text[:-2])   # gets rid of the Euro symbol
            # price has a dot (.) on it and can't convert to int directly
            except ValueError:      
                price = int(float(price_soup.text[:-2]))
            finally:
                return price
        else:
            return price        # returns 0

    def get_ad_description(self, ad_soup):
        """ Returns the description of the ad """
        styles = "cursor:default;text-align: justify;color:#333333;"
        description_soup = ad_soup.find('div', style=styles)
        if description_soup:
            return description_soup.text
        else:
            return ''

    def get_ad_image(self, ad_soup):
        """ Returns the url of the ad image """
        image_text = str(ad_soup.find('img'))
        image_match = re.search(r'src="(.+)" style', image_text)
        if image_match:
            image_url = image_match.group(1)
        else:
            image_url = ''
        return image_url

    def get_ad_dictionary(self, ad_soup):
        """ Constructs an add dictionary to populate the Advertisement model """
        current_ad = dict()
        current_ad['title'] = self.get_ad_title(ad_soup)
        current_ad['subtitle'] = self.get_ad_subtitle(ad_soup)
        current_ad['description'] = self.get_ad_description(ad_soup)
        current_ad['image_url'] = self.get_ad_image(ad_soup)
        current_ad['price'] = self.get_ad_price(ad_soup)
        return current_ad

    def get_all_ads(self):
        """ Populate the self.ads method with ALL categories ads """
        all_ads = []
        start = time.perf_counter()
        for url_name in self.url_names:
            for ad in self.get_category_ads(url_name):
                current_ad = self.get_ad_dictionary(ad)
                current_ad['main_category'] = MainCategory.objects.get(url_name=url_name)
                all_ads.append(current_ad)
        finish = time.perf_counter()
        print(f'Time {round((finish - start), 2)}')
        return all_ads

    def store_ads(self):
        """ Store the ads data into the database """
        Advertisement.objects.all().delete()
        for index, ad in enumerate(self.ads):
            Advertisement.objects.create(**ad)
            print(index)