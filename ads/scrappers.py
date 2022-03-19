import requests
from bs4 import BeautifulSoup
from ads.models import MainCategory, SubCategory
import re


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
    pass