import os
import requests
from google_play_scraper import app, Sort, reviews, reviews_all, search
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

class Play:
    def __init__(self, country='us', app_id=None, search=None):
        self.country = country
        if app_id is not None:
             self.app_id = app_id
        elif search is not None:
            self.app_id = search_app(term=search, store='play', country=country, strategy='id')
        else:
            raise ValueError("Either an app ID or a search term must be provided.")

    def get_details(self):
        result = app(country=self.country, app_id=self.app_id)
        return result

    def get_reviews(self, n_reviews=100, sort='recency'):
        """
        Parameters
        ----------
        n_reviews : str, int (optional)
            The number of reviews to return. 'all' returns all reviews.
            Defaults to 100.
        sort : str (optional)
            The sorting method for the reviews. Choose between 'recency' and 'relevance'.
            Defaults to 'recency'.
        """
        if sort == 'recency':
            if n_reviews == 'all':
                result = reviews_all(self.app_id, count=n_reviews, sort=Sort.NEWEST)
            result, _ = reviews(self.app_id, count=n_reviews, sort=Sort.NEWEST)
            return result
        elif sort == 'relevance':
            if n_reviews == 'all':
                result = reviews_all(self.app_id, count=n_reviews, sort=Sort.MOST_RELEVANT)
            result, _ = reviews(self.app_id, count=n_reviews, sort=Sort.MOST_RELEVANT)
            return result
        else:
            raise ValueError("Invalid sort type. Expected either 'recency' or 'relevance'.")

class Apple:
    def __init__(self, country='us', app_id=None, search=None):
        self.country = country
        if app_id is not None:
            self.app_id = app_id
        elif search is not None:
            self.app_id = search_app(term=search, store='apple', country=country, strategy='id')
        else:
            raise ValueError("Either an app ID or a search term must be provided.")

    def get_details(self):
        SERP_PROD = "https://serpapi.com/search.json?engine=apple_product&"
        result = requests.get(f"{SERP_PROD}country={self.country}&product_id={self.app_id}&api_key={os.getenv('SERP_KEY')}").json()
        return result

    def get_reviews(self, n_reviews=100, sort='recency'):
        """
        Parameters
        ----------
        n_reviews : str, int (optional)
            The number of reviews to return. 'all' returns all reviews.
            Defaults to 100.
        sort : str (optional)
            The sorting method for the reviews. Choose between 'recency' and 'relevance'.
            Defaults to 'recency'.
        """
        SERP_PROD = "https://serpapi.com/search.json?engine=apple_reviews&"
        if sort == 'recency':
            result = requests.get(f"{SERP_PROD}country={self.country}&product_id={self.app_id}&sort=mostrecent&api_key={os.getenv('SERP_KEY')}").json()
            return result
        elif sort == 'relevance':
            result = requests.get(f"{SERP_PROD}country={self.country}&product_id={self.app_id}&sort=mosthelpful&api_key={os.getenv('SERP_KEY')}").json()
            return result
        else:
            raise ValueError("Invalid sort type. Expected either 'recency' or 'relevance'.")
    


def search_app(term, store='play', country='us', strategy='id'):
    """
    Parameters
    ----------
    term : str
        The search term for the app(s).
    store : str
        The app store to search from ('play': Play Store; 'apple': Apple App Store).
        Defaults to 'play'.
    country : str, (optional)
        The country to search from. Defaults to 'us'.
    strategy : str, int (optional)
        The search strategy to use. 'id' returns the id of the most relevant app.
        Integer n from 1 to 30 returns a list of the top n relevant apps.
        Defaults to 'id'.
    """

    store_ls = ['play', 'apple']
    SERP_URL = 'https://serpapi.com/search.json?engine=apple_app_store'
    if strategy == 'id':
        if store == "play":
            result = search(term, country=country, n_hits=1)
            return result[0]['appId']
        elif store == "apple":
            result = requests.get(f"{SERP_URL}&term={term}&country={country}&num={1}&api_key={os.getenv('SERP_KEY')}").json()
            return result['organic_results'][0]['id']  # AppStore requires the app name instead of app id
        else:
            raise ValueError("Invalid store type. Expected one of: %s." % store_ls)
    elif isinstance(strategy, int):
        if store == "play":
            result = search(term, country=country, n_hits=strategy)
            return result
        elif store == "apple":
            result = requests.get(f"{SERP_URL}&term={term}&country={country}&num={strategy}&api_key={os.getenv('SERP_KEY')}").json()
            return result['organic_results']
        else:
            raise ValueError("Invalid store type. Expected one of: %s." % store_ls)
    else:
        raise ValueError("Invalid strategy. Please either enter 'id' or a number.")