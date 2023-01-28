import string
import re
import pandas as pd
import numpy as np
from scipy.stats import skew
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from arcgis.gis import GIS
from arcgis.geocoding import geocode
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('vader_lexicon')

def play_features(data, reviews=None):
    features = ['title', 'appId', 'realInstalls', 'score', 'description', 'ratings', 'reviews', 'histogram', 'price', 'free', 'currency', 'sale',
    'offersIAP', 'inAppProductPrice', 'developerAddress', 'genreId', 'contentRating', 'adSupported', 'containsAds', 'released']
    data_filtered = {k: data[k] for k in data.keys() & set(features)}

    # process histogram
    reviews_dist = np.concatenate([np.full(n, i+1) for i, n in enumerate(data_filtered['histogram'])])
    data_filtered['reviewsStd'] = round(np.std(reviews_dist), 4)
    data_filtered['reviewsSkew'] = round(skew(reviews_dist), 4)

    # process sentiment
    sia = SentimentIntensityAnalyzer()
    data_filtered['descriptionSentiment'] = sia.polarity_scores(process_text(data_filtered['description']))['compound']
    data_filtered['reviewsSentiment'] = process_reviews_sentiment(reviews)

    data_filtered = process_iap(data_filtered)
    data_filtered['developerCountry'] = process_address(data_filtered['developerAddress'])
    data_filtered['releasedYear'] = int(data_filtered['released'][-4:])

    # drop unused features
    data_filtered.pop('histogram')
    return data_filtered

def apple_features(data):
    pass

def process_text(text):
    stop = stopwords.words('english') + list(string.punctuation)
    text_tokenized = word_tokenize(re.sub(r'\d+', '', text))
    text_ls = [txt.lower() for txt in text_tokenized if txt.lower() not in stop]
    processed_text = ' '.join(text_ls)
    return processed_text

def process_iap(data):
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
    if address is None:
        return ""
    else:
        gis = GIS()
        address_processed = re.sub('\n', ' ', address)
        location = geocode(address_processed)
        if location is None:
            return ""
        else:
            return location[0]['attributes']['Country']

def process_reviews_sentiment(reviews):
    reviews_sentiment = []
    sia = SentimentIntensityAnalyzer()
    for review in reviews:
        if review['content'] is not None:
            sentiment = sia.polarity_scores(process_text(review['content']))['compound']
            reviews_sentiment.append(sentiment)
        else:
            pass
    return round(np.mean(reviews_sentiment), 4)
