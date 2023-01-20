import string
import re
import pandas as pd
import numpy as np
from scipy.stats import skew
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('vader_lexicon')

def play_features(data):
    features = ['realInstalls', 'score', 'description', 'ratings', 'reviews', 'histogram', 'price', 'free', 'currency', 'sale',
    'offersIAP', 'inAppProductPrice', 'genreId', 'contentRating', 'adSupported', 'containsAds', 'released']
    data_filtered = {k: data[k] for k in data.keys() & set(features)}
    reviews_dist = np.concatenate([np.full(n, i+1) for i, n in enumerate(data_filtered['histogram'])])
    data_filtered['reviewsStd'] = np.std(reviews_dist)
    data_filtered['reviewsSkew'] = skew(reviews_dist)
    sia = SentimentIntensityAnalyzer()
    data_filtered['descriptionSentiment'] = sia.polarity_scores(process_text(data_filtered['description']))['compound']
    if data_filtered['inAppProductPrice'] is not None:
        data_filtered['IAPMin'] = re.search(r'\$([^ ]+)', data_filtered['inAppProductPrice']).group(1)
        try:
            data_filtered['IAPMax'] = re.search(r'- \$([^p]+)', data_filtered['inAppProductPrice']).group(1)
        except AttributeError:
            data_filtered['IAPMax'] = data_filtered['IAPMin']
    else:
        data_filtered['IAPMin'] = 0
        data_filtered['IAPMax'] = 0
    data_filtered['releasedYear'] = int(data_filtered['released'][-4:])

    data_filtered.pop('histogram')
    data_filtered.pop('description')
    data_filtered.pop('inAppProductPrice')
    data_filtered.pop('released')

    df = pd.DataFrame(data_filtered, index=[0])

    return [df.melt(var_name="Feature", value_name="Value").to_dict('records')]

def apple_features(data):
    pass

def process_text(text):
    stop = stopwords.words('english') + list(string.punctuation)
    text_tokenized = word_tokenize(re.sub(r'\d+', '', text))
    text_ls = [txt.lower() for txt in text_tokenized if txt.lower() not in stop]
    processed_text = ' '.join(text_ls)
    return processed_text
