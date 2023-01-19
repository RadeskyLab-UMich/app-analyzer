import pandas as pd
import numpy as np
from scipy.stats import skew

def play_features(data):
    features = ['realInstalls', 'score', 'ratings', 'reviews', 'histogram', 'price', 'free', 'currency', 'sale',
    'offersIAP', 'inAppProductPrice', 'genreId', 'contentRating', 'adSupported', 'containsAds', 'released']
    data_filtered = {k: data[k] for k in data.keys() & set(features)}
    data_filtered['reviewsStd'] = np.std(data_filtered['histogram'])
    data_filtered['reviewsSkew'] = skew(np.concatenate([np.full(n, i+1) for i, n in enumerate(data_filtered['histogram'])]))
    data_filtered.pop('histogram')
    df = pd.DataFrame(data_filtered, index=[0])
    df['releasedYear'] = pd.to_datetime(df['released']).dt.year
    df['IAPMin'] = df['inAppProductPrice'].str.extract(r'\$([^-]+)')
    df['IAPMax'] = df['inAppProductPrice'].str.extract(r'- \$([^p]+)')
    df.drop(columns=['released', 'inAppProductPrice'], inplace=True)
    return [df.melt(var_name="Feature", value_name="Value").to_dict('records')]

def apple_features(data):
    pass