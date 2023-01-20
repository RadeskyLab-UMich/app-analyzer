import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

dash.register_page(__name__)

features = [
    'title', 'description', 'summary', 'realInstalls', 'score', 'ratings', 'reviews', 'price', 'free', 
    'currency', 'sale', 'offersIAP', 'developer', 'developerId', 'developerWebsite', 'privacyPolicy', 
    'genreId', 'icon', 'headerImage', 'video', 'videoImage', 'contentRating', 'contentRatingDescription', 
    'adSupported', 'containsAds', 'released', 'version', 'recentChanges', 'appId', 'url', 'IAPMin', 'IAPMax', 'releasedYear'
]

features_extra = ['reviewsStd', 'reviewsSkew', 'descriptionSentiment']

filters = dbc.Row(
    [
        dbc.Col(
            dcc.Dropdown(features, multi=True, persistence=True, placeholder="Select base features", id="filters-base")
        ),
        dbc.Col(
            dcc.Dropdown(features_extra, multi=True, persistence=True, placeholder="Select analytical features", id="filters-extra")
        )
    ],
    class_name="g-2 ms-auto flex-wrap mx-auto",
    align="center",
)

play_tab = dbc.Container(
    [
        html.Br(),
        dbc.Textarea(
            className="mb-3", style={"height": "20rem"}, id="dl-input-play",
            placeholder="Enter the app names/IDs for the app features you wish to download. Please place one app per line."
        ),
        dbc.Button(
            "Download as CSV", color="primary", id="dl-button-play", n_clicks=0
        ),
    ]
)

apple_tab = dbc.Container(
    [
        html.Br(),
        dbc.Textarea(
            className="mb-3", style={"height": "20rem"}, id="dl-input-apple",
            placeholder="Enter the app names/IDs for the app features you wish to download. Please place one app per line."
        ),
        dbc.Button(
            "Download as CSV", color="primary", id="dl-button-apple", n_clicks=0
        ),
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
                dbc.Tab(apple_tab, label="Apple App Store", tab_id='apple_tab')
            ],
            active_tab="play_tab",
        )
    ]
)

