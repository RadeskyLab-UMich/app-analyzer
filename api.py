import os
import requests
from google_play_scraper import app, Sort, reviews, reviews_all, search
from app_store_scraper import AppStore
from dotenv import load_dotenv
load_dotenv()

class Play:
    def __init__(self, country, app_id=None, search=None):
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

    def get_reviews(self, n_reviews=100, sort='newest'):
        if sort == 'newest':
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
            raise ValueError("Invalid sort type. Expected either 'newest' or 'relevance'.")

class App:
    def __init__(self, country, app_name=None, app_id=None):
        self.country = country
        if app_name is None:
            pass
        self.app = AppStore(app_name=app_name, country=country)
        if app_id is None:
            app_id = self.app.search_id()
        self.app_id = int(app_id)

    def get_details(self):
        pass

    def get_reviews(self):
        pass


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
            return result['organic_results'][0]['title']  # AppStore requires the app name instead of app id
        else:
            raise ValueError("Invalid store type. Expected one of: %s." % store_ls)
    elif strategy.isnumeric():
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
