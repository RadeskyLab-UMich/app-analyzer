import os
import requests
from google_play_scraper import app, Sort, reviews, reviews_all, search
from itunes_app_scraper.scraper import AppStoreScraper
from dotenv import load_dotenv
load_dotenv()


class Play:
    """
    A class used to represent a Google Play app

    ...

    Attributes
    ----------
    country - str
        a string representing the country code to base the scraping on (default us)
    app_id - str
        the ID of the app (default None)
    search - str
        the term used to search for an app (default None)

    Methods
    -------
    get_details()
        Gets the details of the app
    get_reviews(n_reviews=100, sort=recency)
        Gets the reviews for the app
    """

    def __init__(self, country='us', app_id=None, search=None):
        """
        Parameters
        ----------
        country (str) - optional, defaults to us
        app_id (str) - optional, defaults to None
        search (str) - optional, defaults to None
        """

        self.country = country
        if app_id is not None:
             self.app_id = app_id
        elif search is not None:
            self.app_id = search_app(term=search, store='play', country=country, strategy='id')
        else:
            raise ValueError("Either an app ID or a search term must be provided.")

    def get_details(self):
        """
        Function to scrape data for a Google Play app ID.

        Parameters
        ----------
        None

        Returns
        -------
        result (dict) or None - dictionary of the app containing info such as title, price, etc., or None if not found.
        """

        result = app(country=self.country, app_id=self.app_id)
        return result

    def get_reviews(self, n_reviews=100, sort='recency'):
        """
        Function to get reviews for a specific app.

        Parameters
        ----------
        n_reviews - str, int (optional)
            The number of reviews to return. 'all' returns all reviews.
            Defaults to 100.
        sort - str (optional)
            The sorting method for the reviews. Choose between 'recency' and 'relevance'.
            Defaults to 'recency'.

        Returns
        -------
        result (list) - list of dictionaries of reviews (each review is a dict containing reviewId, userName, content, etc.)
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
    """
    A class used to represent an iTunes / Apple App Store app

    ...

    Attributes
    ----------
    country - str
        a string representing the country code to base the scraping on (default us)
    app_id - str
        the ID of the app (default None)
    search - str
        the term used to search for an app (default None)

    Methods
    -------
    get_details()
        Gets the details of the app
    get_reviews(n_reviews=100, sort=recency)
        Gets the reviews for the app
    """

    def __init__(self, country='us', app_id=None, search=None):
        """
        Parameters
        ----------
        country (str) - optional, defaults to us
        app_id (str) - optional, defaults to None
        search (str) - optional, defaults to None
        """

        self.country = country
        if app_id is not None:
            self.app_id = app_id
        elif search is not None:
            self.app_id = search_app(term=search, store='apple', country=country, strategy='id')
        else:
            raise ValueError("Either an app ID or a search term must be provided.")

    def get_details(self):
        """
        Function to scrape data for a Apple app ID.

        Parameters
        ----------
        None

        Returns
        -------
        result (dict) or None - dictionary of the app containing info such as title, price, etc., or None if not found.
        """
        scraper = AppStoreScraper()
        try:
            result = scraper.get_app_details(self.app_id, country=self.country, lang="en")
            return result
        except:
            raise ValueError('App details not found.')

    def get_reviews(self, n_reviews=50, sort='recency'):
        """
        Function to get reviews for a specific app.

        Parameters
        ----------
        n_reviews - str, int (optional)
            The number of reviews to return.
            Defaults to 50.
        sort - str (optional)
            The sorting method for the reviews. Choose between 'recency' and 'relevance'.
            Defaults to 'recency'.

        Returns
        -------
        result (list) - list of nested dictionaries of reviews (each review is a dicr containing author, name, content, etc.)
        """

        # SERP_REVIEW = "https://serpapi.com/search.json?engine=apple_reviews&"
        REVIEW_URL = "https://itunes.apple.com/rss/customerreviews/"
        if sort == 'recency':
            # result = requests.get(f"{SERP_REVIEW}country={self.country}&product_id={self.app_id}&sort=mostrecent&api_key={os.getenv('SERP_KEY')}").json()
            result = requests.get(f"{REVIEW_URL}id={self.app_id}/sortBy=mostRecent/json").json()
            return result['feed']['entry']
        elif sort == 'relevance':
            # result = requests.get(f"{SERP_REVIEW}country={self.country}&product_id={self.app_id}&sort=mosthelpful&api_key={os.getenv('SERP_KEY')}").json()
            result = requests.get(f"{REVIEW_URL}id={self.app_id}/sortBy=mostHelpful/json").json()
            return result['feed']['entry']
        else:
            raise ValueError("Invalid sort type. Expected either 'recency' or 'relevance'.")





def search_app(term, store='play', country='us', strategy='id'):
    """
    Parameters
    ----------
    term - str
        The search term for the app(s).
    store - str
        The app store to search from ('play': Play Store; 'apple': Apple App Store).
        Defaults to 'play'.
    country - str, (optional)
        The country to search from. Defaults to 'us'.
    strategy - str, int (optional)
        The search strategy to use. 'id' returns the id of the most relevant app.
        Integer n from 1 to 30 returns a list of the top n relevant apps.
        Defaults to 'id'.

    Returns
    -------
    str or list of IDs for term of app search
    """

    store_ls = ['play', 'apple']
    SERP_URL = 'https://serpapi.com/search.json?engine=apple_app_store'
    scraper = AppStoreScraper()
    if strategy == 'id':
        if store == "play":
            result = search(term, country=country, n_hits=1)
            return result[0]['appId']
        elif store == "apple":
            try:
                result = scraper.get_app_ids_for_query(term, num=1, country=country, lang="en")
                return result[0]
            except:
                try:
                    result = requests.get(f"{SERP_URL}&term={term}&country={country}&num={1}&api_key={os.getenv('SERP_KEY')}").json()
                    return result['organic_results'][0]['id']  # AppStore requires the app name instead of app id
                except:
                    raise ValueError("App not found.")
        else:
            raise ValueError("Invalid store type. Expected one of: %s." % store_ls)
    elif isinstance(strategy, int):
        if store == "play":
            result = search(term, country=country, n_hits=strategy)
            return result
        elif store == "apple":
            try:
                result = scraper.get_app_ids_for_query(term, num=strategy, country=country, lang="en")
            except:
                try:
                    result = requests.get(f"{SERP_URL}&term={term}&country={country}&num={strategy}&api_key={os.getenv('SERP_KEY')}").json()
                except:
                    raise ValueError("App not found.")
            return result
        else:
            raise ValueError("Invalid store type. Expected one of: %s." % store_ls)
    else:
        raise ValueError("Invalid strategy. Please either enter 'id' or a number.")