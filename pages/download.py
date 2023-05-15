import time
import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash.dependencies import Input, Output, State
from api import Play, Apple
from utils import *

dash.register_page(__name__)

features = ['title', 'appId', 'realInstalls', 'score', 'description', 'ratings', 'reviews', 'histogram', 'price', 'free', 'currency', 'sale',
'offersIAP', 'inAppProductPrice', 'developerId', 'developerAddress', 'genre', 'genreId', 'contentRating', 'contentRatingDescription', 'adSupported', 'containsAds', 'released']

features_derived = ['ratingsStd', 'ratingsSkew', 'descriptionSentiment', 'reviewsSentiment', 'descriptionReadability', 'descriptionGrammar', 
'developerNApps', 'developerAppAgeMedian', 'developerCountry', 'releasedYear']

filters = dbc.Row(
    [
        dbc.Col(
            dcc.Dropdown(sorted(features), value=['title', 'appId'], persistence=True, multi=True, placeholder="Select base features", id="filters-base")
        ),
        dbc.Col(
            dcc.Dropdown(sorted(features_derived), persistence=True, multi=True, placeholder="Select derived features", id="filters-derived")
        ),
        # dbc.Col(dmc.Checkbox(id="predict-checkbox", label="Include predictions"), width="auto")
    ],
    class_name="g-2 ms-auto flex-wrap mx-auto",
    align="center",
    style={"width": "1000px"}
)

play_tab = dbc.Container(
    [
        html.Br(),
        dbc.Textarea(
            className="mb-3", style={"height": "20rem"}, id="dl-input-play",
            placeholder="Enter the app IDs for the app features you wish to download. Please place one app per line."
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
                )
            ],
            class_name="g-2",
            align='center'
        ),
        dcc.Store(id="dl-temp-play", storage_type='session')
    ]
)

apple_tab = dbc.Container(
    [
        html.Br(),
        dbc.Textarea(
            className="mb-3", style={"height": "20rem"}, id="dl-input-apple",
            placeholder="Enter the app IDs for the app features you wish to download. Please place one app per line."
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
                    width="auto"
                )
            ],
            class_name="g-1"
        ),
        dcc.Store(id="dl-temp-apple", storage_type='session')
    ]
) 

layout = dbc.Container(
    [
        html.Br(),
        filters,
        html.Br(),
        dbc.Tabs(
            [
                dbc.Tab(play_tab, label="Play Store", tab_id='play_tab', tab_style={'marginLeft':'auto'}),
                dbc.Tab(apple_tab, label="Apple App Store", tab_id='apple_tab', disabled=True)
            ],
            active_tab="play_tab",
        )
    ]
)

@dash.callback(
    Output('dl-temp-play', 'data'),
    [
        Input('confirm-button-play', 'n_clicks'),
        # Input('predict-checkbox', 'checked'),
    ],
    State('dl-input-play', 'value'),
    running=[
        (Output("dl-button-play", "disabled"), True, False),
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
def update_play_info(set_progress, click, apps):
    full_play_ls = []
    not_found = []
    apps_ls = apps.split('\n')
    n_apps = len(apps_ls)
    for idx, app_id in enumerate(apps_ls):
        print(f"Fetching {idx + 1}/{n_apps}: {app_id}")
        set_progress((idx + 1, f"{int((idx + 1) / n_apps * 100)} %", n_apps))
        try:
            app_info = Play(app_id=app_id.strip())
            play_details = app_info.get_details()
            time.sleep(0.5)
            play_reviews = app_info.get_reviews(sort='relevance')
            play_info = play_features(play_details, play_reviews)
            # if predict:
            #     pass
            full_play_ls.append(play_info)
        except Exception as e:
            print(e)
            not_found.append(app_id)
        time.sleep(0.5)
    
    return full_play_ls

@dash.callback(
    Output('dl-play', 'data'),
    Input('dl-button-play', 'n_clicks'),
    [
        State('dl-temp-play', 'data'),
        State('filters-base', 'value'),
        State('filters-derived', 'value')
    ],
    prevent_initial_call=True
)
def play_download(click, data, base, derived):
    filters = list(base) + list(derived)
    df = pd.DataFrame(data)
    df.drop(columns=df.columns.difference(filters), inplace=True)

    return dcc.send_data_frame(df.to_csv, "play_features.csv", index=False)