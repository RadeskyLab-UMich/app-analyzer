import requests
from google_play_scraper import app, Sort, reviews, reviews_all, search
from app_store_scraper import AppStore
import os
from dotenv import load_dotenv
load_dotenv()

class App:
    def __init__(self):
        pass

    def get_details():
        pass

    def get_reviews():
        pass

class Play:
    def __init__(self):
        pass

    def get_details():
        pass

    def get_reviews():
        pass


def search_app(term, os='play', country='us', strategy='id'):
    """
    Parameters
    ----------
    term : str
        The search term for the app(s).
    os : str
        The app store to search from ('play': Play Store; 'ios': iOS App Store).
        Defaults to 'play'.
    country : str, (optional)
        The country to search from. Defaults to 'us'.
    strategy : str, int (optional)
        The search strategy to use. 'id' returns the id of the most relevant app.
        Integer n from 1 to 30 returns a list of the top n relevant apps.
        Defaults to 'id'.
    """

    os_ls = ['play', 'ios']
    SERP_URL = 'https://serpapi.com/search.json?engine=apple_app_store'
    if strategy == 'id':
        if os == "play":
            result = search(term, country=country, n_hits=1)
            return result[0]['appId']
        elif os == "ios":
            result = requests.get(f"{SERP_URL}&term={term}&country={country}&num={1}&api_key={os.getenv('SERP_KEY')}").json()
            return result['organic_results'][0]['id']
        else:
            raise ValueError("Invalid OS type. Expected one of: %s" % os_ls)
    elif strategy.isnumeric():
        if os == "play":
            result = search(term, country=country, n_hits=strategy)
            return result
        elif os == "ios":
            result = requests.get(f"{SERP_URL}&term={term}&country={country}&num={strategy}&api_key={os.getenv('SERP_KEY')}").json()
            return result['organic_results']
        else:
            raise ValueError("Invalid OS type. Expected one of: %s" % os_ls)
    else:
        raise ValueError("Invalid strategy. Please either enter 'id' or a number.")
