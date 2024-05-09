import time
import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash.dependencies import Input, Output, State
from api import Play, Apple
from utils import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import language_tool_python

dash.register_page(__name__)

features = ['title', 'appId', 'realInstalls', 'score', 'developer', 'version', 'description', 'ratings', 'reviews', 'price', 'free', 'currency', 'sale',
'offersIAP', 'inAppProductPrice', 'developerId', 'developerAddress', 'genre', 'genreId', 'contentRating', 'contentRatingDescription', 'adSupported', 'containsAds', 'released']

features_derived = ['ratingsStd', 'ratingsSkew', 'descriptionSentiment', 'reviewsSentiment', 'descriptionReadability', 'descriptionGrammar', 
'developerNApps', 'developerAppAgeMedian', 'developerCountry', 'releasedYear']

# filters = dbc.Row(
#     [
#         dbc.Col(
#             dcc.Dropdown(sorted(features), value=['title', 'appId'], persistence=True, multi=True, placeholder="Select base features", id="filters-base")
#         ),
#         dbc.Col(
#             dcc.Dropdown(sorted(features_derived), persistence=True, multi=True, placeholder="Select derived features", id="filters-derived")
#         ),
#         dbc.Col(dmc.Checkbox(id="predict-checkbox", label="Include predictions"), width="auto")
#     ],
#     class_name="g-2 ms-auto flex-wrap mx-auto",
#     align="center",
#     style={"width": "1000px"}
# )

play_tab = dbc.Container(
    [
        dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(sorted(features), value=['title', 'appId'], persistence=True, multi=True, placeholder="Select base features", id="filters-base")
            ),
            dbc.Col(
                dcc.Dropdown(sorted(features_derived), persistence=True, multi=True, placeholder="Select derived features", id="filters-derived")
            ),
            dbc.Col(dmc.Checkbox(id="predict-checkbox", label="Include predictions"), width="auto")
        ],
        class_name="g-2 ms-auto flex-wrap mx-auto",
        align="center",
        style={"width": "1000px"}
        ),
        html.Br(),
        dbc.Textarea(
            className="mb-3", style={"height": "20rem"}, id="dl-input-play",
            placeholder="Enter the app IDs for the app features you wish to download. Please place one app per line.\nEx:\ncom.duolingo\nvitaminshoppe.consumerapp"
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button("Confirm", color="primary", id="confirm-button-play", n_clicks=0),
                    width="auto"
                ),
                dbc.Col(
                    [
                        dbc.Button("Download as CSV", color="secondary", id="dl-button-play", n_clicks=0, disabled=True),
                        dcc.Download(id="dl-play")
                    ],
                    width="auto"
                ),
                dbc.Col(
                    dbc.Progress(id="dl-play-progress", style={"height": "2rem"}, animated=True, striped=True),
                    width=3
                ),
                dbc.Col(
                    [
                        dbc.Button("Download Missing IDs", color="success", id="dl-button-play2", n_clicks=0, disabled=True),
                        dcc.Download(id="dl-play2")
                    ],
                    width="auto"
                ),
            ],
            class_name="g-2",
            align='center'
        ),
        dcc.Store(id="dl-temp-play", storage_type='session'),
        dcc.Store(id="dl-temp-play-none", storage_type='session')
    ]
)

apple_tab = dbc.Container(
    [
        html.Br(),
        dbc.Textarea(
            className="mb-3", style={"height": "20rem"}, id="dl-input-apple",
            placeholder="Enter the app IDs for the app features you wish to download. Please place one app per line.\nEx:\n1024722275\n1448010566"
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button("Confirm", color="primary", id="confirm-button-apple", n_clicks=0),
                    width="auto"
                ),
                dbc.Col(
                    [
                        dbc.Button("Download as CSV", color="secondary", id="dl-button-apple", n_clicks=0, disabled=True),
                        dcc.Download(id="dl-apple")
                    ],
                    width="auto"
                ),
                dbc.Col(
                    dbc.Progress(id="dl-apple-progress", style={"height": "2rem"}, animated=True, striped=True),
                    width=3
                ),
                dbc.Col(
                    [
                        dbc.Button("Download Missing IDs", color="success", id="dl-button-apple2", n_clicks=0, disabled=True),
                        dcc.Download(id="dl-apple2")
                    ],
                    width="auto"
                )
            ],
            class_name="g-1"
        ),
        dcc.Store(id="dl-temp-apple", storage_type='session'),
        dcc.Store(id="dl-temp-apple-none", storage_type='session')
    ]
)

layout = dbc.Container(
    [
        html.Br(),
        dbc.Tabs(
            [
                dbc.Tab(play_tab, label="Play Store", tab_id='play_tab', tab_style={'marginLeft':'auto'}),
                dbc.Tab(apple_tab, label="Apple App Store", tab_id='apple_tab')
            ],
            active_tab="play_tab",
        )
    ]
)

@dash.callback(
    Output('dl-temp-play', 'data'),
    Output('dl-temp-play-none', 'data'),
    [
        Input('confirm-button-play', 'n_clicks'),
    ],
    [
        State('predict-checkbox', 'checked'),
        State('dl-input-play', 'value'),
        State('filters-base', 'value'), # added
        State('filters-derived', 'value') # added
    ],
    running=[
        (Output("dl-button-play", "disabled"), True, False),
        (Output("dl-button-play2", "disabled"), True, False),
        (Output("dl-play-progress", "animated"), True, False),
    ],
    progress=[
        Output("dl-play-progress", "value"),
        Output("dl-play-progress", "label"),
        Output("dl-play-progress", "max")
    ],
    prevent_initial_call=True,
    background=True
)
def update_play_info(set_progress, click, predict, apps, base, derived):
    full_play_ls = []
    not_found = []
    not_found2 = []
    apps_ls = apps.split('\n')
    n_apps = len(apps_ls)

    tool = language_tool_python.LanguageTool('en-US')

    for idx, app_id in enumerate(apps_ls):
        print(f"Fetching {idx + 1}/{n_apps}: {app_id}")
        set_progress((idx + 1, f"{int((idx + 1) / n_apps * 100)} %", n_apps))
        try:
            app_info = Play(app_id=app_id.strip())
            play_info = app_info.get_details()
            time.sleep(0.5)
            if derived:
                if "reviewsSentiment" in derived: # added
                    reviews = app_info.get_reviews(sort='relevance')
                    if len(reviews) > 0:
                        play_info['reviewsSentiment'] = process_reviews_sentiment(reviews)
                    else:
                        play_info['reviewsSentiment'] = np.nan

                if "ratingsStd" in derived or "ratingsSkew" in derived: # added
                    # process histogram
                    reviews_dist = np.concatenate([np.full(n, i+1) for i, n in enumerate(play_info['histogram'])])

                    if len(reviews_dist) > 0:
                        play_info['ratingsStd'] = round(np.std(reviews_dist), 4)
                        play_info['ratingsSkew'] = round(skew(reviews_dist, nan_policy='omit'), 4)
                    else:
                        play_info['ratingsStd'] = np.nan
                        play_info['ratingsSkew'] = np.nan

                if "descriptionGrammar" in derived:
                    matches = tool.check(play_info["description"])
                    play_info['descriptionGrammar'] = round((len(play_info["description"]) - len(matches))/len(play_info["description"]) * 100, 2)
                if "descriptionReadability" in derived:
                    play_info['descriptionReadability'] = textstat.flesch_kincaid_grade(play_info['description'])
                if "descriptionSentiment" in derived:
                    sia = SentimentIntensityAnalyzer()
                    play_info['descriptionSentiment'] = sia.polarity_scores(process_text(play_info['description']))['compound']
                if "developerCountry" in derived:
                    play_info['developerCountry'] = process_address(play_info['developerAddress'])
                if "developerNApps" in derived or "developerAppAgeMedian" in derived:
                    play_info['developerNApps'], play_info['developerAppAgeMedian'] = process_developer(play_info['developerId'])
                if play_info['released']:
                    play_info['releasedYear'] = int(play_info['released'][-4:])
                    play_info['releasedYears'] = datetime.now().year - play_info['releasedYear']

            if predict:
                pred_e = generate_predictions(play_info, 'educational')
                pred_v = generate_predictions(play_info, 'violent')
                play_info['educational_proba'] = pred_e
                play_info['violent_proba'] = pred_v
            full_play_ls.append(play_info)
        except Exception as e:
            print(e)
            not_found.append(app_id)
        time.sleep(0.5)

    for app_id in not_found:
        try:
            app_info = Play(app_id=app_id.strip())
            play_info = app_info.get_details()
            time.sleep(0.5)

            if derived:
                if "reviewsSentiment" in derived: # added
                    reviews = app_info.get_reviews(sort='relevance')
                    if len(reviews) > 0:
                        play_info['reviewsSentiment'] = process_reviews_sentiment(reviews)
                    else:
                        play_info['reviewsSentiment'] = np.nan

                if "ratingsStd" in derived or "ratingsSkew" in derived: # added
                    # process histogram
                    reviews_dist = np.concatenate([np.full(n, i+1) for i, n in enumerate(play_info['histogram'])])

                    if len(reviews_dist) > 0:
                        play_info['ratingsStd'] = round(np.std(reviews_dist), 4)
                        play_info['ratingsSkew'] = round(skew(reviews_dist, nan_policy='omit'), 4)
                    else:
                        play_info['ratingsStd'] = np.nan
                        play_info['ratingsSkew'] = np.nan

                if "descriptionGrammar" in derived:
                    matches = tool.check(play_info["description"])
                    play_info['descriptionGrammar'] = round((len(play_info["description"]) - len(matches))/len(play_info["description"]) * 100, 2)
                if "descriptionReadability" in derived:
                    play_info['descriptionReadability'] = textstat.flesch_kincaid_grade(play_info['description'])
                if "descriptionSentiment" in derived:
                    sia = SentimentIntensityAnalyzer()
                    play_info['descriptionSentiment'] = sia.polarity_scores(process_text(play_info['description']))['compound']
                if "developerCountry" in derived:
                    play_info['developerCountry'] = process_address(play_info['developerAddress'])
                if "developerNApps" in derived or "developerAppAgeMedian" in derived:
                    play_info['developerNApps'], play_info['developerAppAgeMedian'] = process_developer(play_info['developerId'])
                if play_info['released']:
                    play_info['releasedYear'] = int(play_info['released'][-4:])
                    play_info['releasedYears'] = datetime.now().year - play_info['releasedYear']

            if predict:
                pred_e = generate_predictions(play_info, 'educational')
                pred_v = generate_predictions(play_info, 'violent')
                play_info['educational_proba'] = pred_e
                play_info['violent_proba'] = pred_v
            full_play_ls.append(play_info)
        except Exception as e:
            print(e)
            not_found2.append(app_id)
        time.sleep(0.5)

    tool.close()

    return full_play_ls, not_found2

@dash.callback(
    Output('dl-play', 'data'),
    Input('dl-button-play', 'n_clicks'),
    [
        State('dl-temp-play', 'data'),
        State('predict-checkbox', 'checked'),
        State('filters-base', 'value'),
        State('filters-derived', 'value')
    ],
    prevent_initial_call=True
)
def play_download(click, data, predict, base, derived):
    if not base and not derived:
        df = pd.DataFrame(data)
        return dcc.send_data_frame(df.to_csv, "play_features.csv", index=False)
    elif not base:
        filters = derived
    elif not derived:
        filters = base
    else:
        filters = base + derived

    if predict:
        filters = filters + ['educational_proba', 'violent_proba']

    df = pd.DataFrame(data)
    df.drop(columns=df.columns.difference(filters), inplace=True)

    return dcc.send_data_frame(df.to_csv, "play_features.csv", index=False)


@dash.callback(
    Output('dl-play2', 'data'),
    Input('dl-button-play2', 'n_clicks'),
    State('dl-temp-play-none', 'data'),
    prevent_initial_call=True
)
def play_download2(click, not_found):
    df = pd.DataFrame({"appId": not_found})

    return dcc.send_data_frame(df.to_csv, "play_features_not_found.csv", index=False)


@dash.callback(
    Output('dl-temp-apple', 'data'),
    Output('dl-temp-apple-none', 'data'),
    [
        Input('confirm-button-apple', 'n_clicks'),
    ],
    [
        State('predict-checkbox', 'checked'),
        State('dl-input-apple', 'value'),
    ],
    running=[
        (Output("dl-button-apple", "disabled"), True, False),
        (Output("dl-button-apple2", "disabled"), True, False),
        (Output("dl-apple-progress", "animated"), True, False),
    ],
    progress=[
        Output("dl-apple-progress", "value"),
        Output("dl-apple-progress", "label"),
        Output("dl-apple-progress", "max")
    ],
    prevent_initial_call=True,
    background=True
)
def update_apple_info(set_progress, click, predict, apps):
    full_apple_ls = []
    not_found = []
    apps_ls = apps.split('\n')
    n_apps = len(apps_ls)
    for idx, app_id in enumerate(apps_ls):
        print(f"Fetching {idx + 1}/{n_apps}: {app_id}")
        set_progress((idx + 1, f"{int((idx + 1) / n_apps * 100)} %", n_apps))
        try:
            app_info = Apple(app_id=app_id.strip())
            apple_details = app_info.get_details()
            time.sleep(0.5)
            #apple_reviews = app_info.get_reviews(sort='relevance')

            #play_info = play_features(play_details, play_reviews)
            #apple_info = play_features(apple_details, apple_reviews)
            #if predict:
            #    pred_e = generate_predictions(apple_info, 'educational')
            #    pred_v = generate_predictions(apple_info, 'violent')
            #    apple_info['educational_proba'] = pred_e
            #    apple_info['violent_proba'] = pred_v
            #full_apple_ls.append(apple_info)
            full_apple_ls.append(apple_details)
        except Exception as e:
            print(e)
            not_found.append(app_id)
        time.sleep(0.5)

    return full_apple_ls, not_found

@dash.callback(
    Output('dl-apple', 'data'),
    Input('dl-button-apple', 'n_clicks'),
    [
        State('dl-temp-apple', 'data'),
        State('predict-checkbox', 'checked'),
        State('filters-base', 'value'),
        State('filters-derived', 'value')
    ],
    prevent_initial_call=True
)
def apple_download(click, data, predict, base, derived):
    df = pd.DataFrame(data)

    return dcc.send_data_frame(df.to_csv, "apple_features.csv", index=False)

@dash.callback(
    Output('dl-apple2', 'data'),
    Input('dl-button-apple2', 'n_clicks'),
    State('dl-temp-apple-none', 'data'),
    prevent_initial_call=True
)
def apple_download2(click, not_found):
    df = pd.DataFrame({"appId": not_found})

    return dcc.send_data_frame(df.to_csv, "apple_features_not_found.csv", index=False)