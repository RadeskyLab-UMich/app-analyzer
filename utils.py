import string
import re
import os
import requests
import pandas as pd
import numpy as np
from scipy.stats import skew
from datetime import datetime

import nltk
import textstat
import language_tool_python
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('vader_lexicon')
stopwords.ensure_loaded()

import googlemaps
from itunes_app_scraper.scraper import AppStoreScraper
from bs4 import BeautifulSoup
from api import Play, Apple
from joblib import load
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

from dotenv import load_dotenv
load_dotenv()




def play_features(data, reviews=None):
    '''
    Function to get the base and derived features of a Play Store app.

    Parameters
    ----------
    data: dict
        Play Store data retrieved with the `get_details` method.
    reviews: list (optional)
        List of Play Store reviews retrieved with the `get_reviews` method.

    Returns
    -------
    dict of the base and derived features of a Play Store app
    '''

    features = ['title', 'appId', 'realInstalls', 'score', 'developer', 'version', 'description', 'ratings', 'reviews', 'histogram', 'price', 'free', 'currency', 'sale',
    'offersIAP', 'inAppProductPrice', 'developerId', 'developerAddress', 'genre', 'genreId', 'contentRating', 'contentRatingDescription', 'adSupported', 'containsAds', 'released']
    data_filtered = {k: data[k] for k in data.keys() & set(features)}

    # process histogram
    reviews_dist = np.concatenate([np.full(n, i+1) for i, n in enumerate(data_filtered['histogram'])])
    if len(reviews_dist) > 0:
        data_filtered['ratingsStd'] = round(np.std(reviews_dist), 4)
        data_filtered['ratingsSkew'] = round(skew(reviews_dist, nan_policy='omit'), 4)
    else:
        data_filtered['ratingsStd'] = np.nan
        data_filtered['ratingsSkew'] = np.nan

    # process text & sentiment
    sia = SentimentIntensityAnalyzer()
    data_filtered['descriptionSentiment'] = sia.polarity_scores(process_text(data_filtered['description']))['compound']
    data_filtered['reviewsSentiment'] = process_reviews_sentiment(reviews)
    data_filtered['descriptionReadability'] = textstat.flesch_kincaid_grade(data_filtered['description'])
    data_filtered['descriptionGrammar'] = process_grammar(data_filtered['description'])
    if len(reviews) > 0:
        data_filtered['reviewsSentiment'] = process_reviews_sentiment(reviews)
    else:
        data_filtered['reviewsSentiment'] = np.nan

    data_filtered = process_iap(data_filtered)
    data_filtered['developerNApps'], data_filtered['developerAppAgeMedian'] = process_developer(data_filtered['developerId'])
    data_filtered['developerCountry'] = process_address(data_filtered['developerAddress'])
    if data_filtered['released']:
        data_filtered['releasedYear'] = int(data_filtered['released'][-4:])
        data_filtered['releasedYears'] = datetime.now().year - data_filtered['releasedYear']

    # drop unused features
    data_filtered.pop('histogram')
    return data_filtered

# def apple_features(data):
#     '''
#     Returns the base and derived features of a App Store app in a dictionary.
#     '''
#     features = ['trackName', 'trackId', 'bundleId', 'isGameCenterEnabled', 'advisories', 'features', 'kind', 'averageUserRating', 'description', 'contentAdvisoryRating',
#                 'releaseDate', 'genres', 'genreIds', 'primaryGenreName', 'primaryGenreId', 'currency', 'artistId', 'price', 'userRatingCount']
#     data_filtered = {k: data[k] for k in data.keys() & set(features)}

#     return data_filtered


def process_text(text):
    '''
    Function to tokenize and clean text for further analyses.

    Parameters
    ----------
    text (str) - str of text (in this case, usually the description of an app)

    Returns
    -------
    str of the processed text
    '''

    stop = stopwords.words('english') + list(string.punctuation)
    text_tokenized = word_tokenize(re.sub(r'\d+', '', text))
    text_ls = [txt.lower() for txt in text_tokenized if txt.lower() not in stop]
    processed_text = ' '.join(text_ls)
    return processed_text


def process_iap(data):
    '''
    Function to get the max and min in-app purchase prices.

    Parameters
    ----------
    data (dict) - dict of the app's data

    Returns
    -------
    data with new columns of min and max IAP
    '''

    if data['inAppProductPrice'] is not None:
        data['IAPMin'] = re.search(r'\$([^ ]+)', data['inAppProductPrice']).group(1)
        try:
            data['IAPMax'] = re.search(r'- \$([^p]+)', data['inAppProductPrice']).group(1)
        except AttributeError:
            data['IAPMax'] = data['IAPMin']
    else:
        data['IAPMin'] = 0
        data['IAPMax'] = 0
    return data


def process_address(address):
    '''
    Function to get the country code of a given address using Google's Geocoding API.

    Parameters
    ----------
    address (str) - developer address of an app

    Returns
    -------
    str of country code
    '''

    if address is None:
        return "Unlisted"
    else:
        # gis = GIS()
        gmaps = googlemaps.Client(key=os.getenv('GMAP_KEY'))
        address_processed = re.sub('\n', ' ', address)
        location = gmaps.geocode(address_processed)
        if len(location) == 0:
            return "Unlisted"
        else:
            country = [i['short_name'] for i in location[0]['address_components'] if 'country' in i['types']]

            if country:
                return country[0]
            else:
                return "Unlisted"


def process_reviews_sentiment(reviews):
    '''
    Function to process the average review sentiment of a given list of reviews obtained with the `get_reviews` method.

    Parameters
    ----------
    reviews (list) - list of reviews for an app

    Returns
    -------
    float of the average sentiment of the reviews
    '''

    reviews_sentiment = []
    sia = SentimentIntensityAnalyzer()
    for review in reviews:
        if review['content'] is not None:
            sentiment = sia.polarity_scores(process_text(review['content']))['compound']
            reviews_sentiment.append(sentiment)
        else:
            pass
    return round(np.mean(reviews_sentiment), 4)


def process_grammar(text):
    '''
    Function to get the grammatical error rate of a given piece of text.

    Parameters
    ----------
    text (str) - str of text (in this case, usually the description of an app)

    Returns
    -------
    float of grammatical error rate of the text
    '''

    tool = language_tool_python.LanguageToolPublicAPI('en-US')
    # tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    tool.close()
    return round((len(text) - len(matches))/len(text) * 100, 2)


def process_developer(id, store="play"):
    '''
    Function to get the number of apps a developer has published on a specific store and the median ages for the app.

    Parameters
    ----------
    id (int) - Developer ID
    store (str) - (optional) Store to fetch data from ('play': Play Store; 'apple': Apple App Store). Defaults to 'play'

    Returns
    -------
    int of number of apps, int of median age for the apps
    '''

    store_ls = ['play', 'apple']
    if store == "play":
        base_url = "https://play.google.com/store/apps/"
        if requests.get(base_url + f"dev?id={id}").status_code == 200:
            developer_content = requests.get(base_url + f"dev?id={id}").text
            developer_soup = BeautifulSoup(developer_content, 'html.parser')
            developer_apps = developer_soup.select('.fUEl2e > div > div > div > a')
        elif requests.get(base_url + f"developer?id={id}").status_code == 200:
            developer_content = requests.get(base_url + f"developer?id={id}").text
            developer_soup = BeautifulSoup(developer_content, 'html.parser')
            developer_apps = developer_soup.select('.fUEl2e > div > div > div > div > a')
        else:
            raise ValueError("Developer ID not found.")
        n_apps = len(developer_apps)
        app_ids = list(map(lambda x: x['href'].split('?id=')[1], developer_apps))
        app_ages = []
        for id in app_ids:
            app_details = Play(app_id=id).get_details()
            if app_details['released'] is not None:
                app_age = (datetime.today() - datetime.strptime(app_details['released'], '%b %d, %Y')).days / 365.25
                app_ages.append(app_age)
            else:
                pass
        return n_apps, round(np.median(app_ages), 1)
    elif store == "apple":
        apple_scraper = AppStoreScraper()
        app_ids = apple_scraper.get_app_ids_for_developer(id, country="us", lang="en")
        n_apps = len(app_ids)
        app_ages = []
        for id in app_ids:
            app_details = apple_scraper.get_app_details(id, country='us', lang="en")
            if app_details['releaseDate'] is not None:
                app_age = (datetime.today() - datetime.strptime(app_details['releaseDate'], '%Y-%m-%dT%H:%M:%SZ')).days / 365.25
                app_ages.append(app_age)
            else:
                pass
        return n_apps, round(np.median(app_ages), 1)
    else:
        raise ValueError("Invalid store type. Expected one of: %s." % store_ls)


def generate_predictions(data, target='educational'):
    '''
    Function that, given a set of features obtained with the `play_features` function, generates the predicted probability that the app fits the target label.

    Parameters
    ----------
    data (dict) - Feature dictionary generated using the `play_features` function
    target (str) - (optional) Predict whether or not the given app is 'educational' or 'violent'

    Returns
    -------
    float of the prediction of the target variable/feature
    '''

    target_ls = ['educational', 'violent']
    num_columns = ['realInstalls', 'price', 'ratings', 'reviews', 'score', 'ratingsStd', 'ratingsSkew', 'descriptionSentiment', 'reviewsSentiment', 'descriptionReadability', 'descriptionGrammar', 'developerNApps', 'developerAppAgeMedian', 'releasedYears']
    cat_columns = ['genreId', 'contentRating'] # , 'developerCountry'
    bool_columns = ['offersIAP', 'sale', 'containsAds', 'free', 'adSupported']
    data_filtered = {k: v for k, v in data.items() if k in num_columns + cat_columns + bool_columns}
    scaler = StandardScaler()
    data_processed = pd.DataFrame(data_filtered.copy(), index=[0])
    data_processed[num_columns] = scaler.fit_transform(data_processed[num_columns])
    data_processed = pd.get_dummies(data_processed)

    if target == 'educational':
        model = load('models/rf_e_0607.joblib')
        model_features = pd.read_csv('models/features_educational.csv')
    elif target == 'violent':
        model = load('models/rf_v_0607.joblib')
        model_features = pd.read_csv('models/features_violent.csv')
    else:
        raise ValueError("Invalid target. Expected one of: %s." % target_ls)
    model_features, data_processed = model_features.align(data_processed, join='left', axis=1, fill_value=0)
    pred = model.predict_proba(data_processed)[:,1][0]

    return pred