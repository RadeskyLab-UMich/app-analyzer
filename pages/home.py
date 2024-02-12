import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from api import Play, Apple
from utils import *

dash.register_page(__name__, path='/')

search_bar = dbc.Row(
    [
        dbc.Col(
            html.Div(
                [
                    html.I(className="fa-solid fa-circle-info"),
                    html.P(
                        '''Search with Play Store app ID - play: <id>\
                        \nSearch with App Store app title - apple: <title>\
                        \nSearch with keywords - <keywords>''',
                        className='info',
                        style={'width': '18rem'}
                    )
                ],
                className="tooltip"
            ),
            width=1
        ),
        dbc.Col(
            dcc.Dropdown(["Play", "Apple"], value=["Play"], id='search-type')
        ),
        dbc.Col(
            dbc.Input(id="search-term", type="search", placeholder="Enter an app ID or keywords", value="com.mojang.minecraftpe"),
        ),
        dbc.Col(
            dbc.Button(
                "Search", color="primary", class_name="ms-2",
                id="search-button", n_clicks=0
            ),
            width="auto",
        ),
        dcc.Store(id='search-temp', storage_type='session'),
        dcc.Store(id='details-temp', storage_type='session'),
        dcc.Store(id='reviews-temp', storage_type='session')
    ],
    class_name="g-0 ms-auto flex-wrap mx-auto",
    align="center",
    style={'width': '600px'}
)

play_tab = dbc.Row(
    [
        dbc.Col(
            [
                html.Br(),
                dcc.Loading(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(id='play-img', height="55px"), width="auto", style={"margin": "auto"}
                                ),
                                dbc.Col(
                                    [
                                        html.H2(html.A(id='play-title', target="_blank")),
                                        html.H6(["App ID: ", html.Span(id='play-id')]),
                                    ]
                                )
                            ]
                        ),
                        dt.DataTable(
                            id='play-details',
                            columns=[
                                {"name": "Feature", "id": "Feature"},
                                {"name": "Value", "id": "Value"}
                            ],
                            style_as_list_view=True,
                            style_cell={'fontSize': '1rem', 'textAlign': 'left', 'paddingRight': '2rem', 'fontFamily': "Helvetica Neue"},
                            style_header={'fontWeight': 'bold', 'backgroundColor': '#808080', 'color': 'white'},
                            fill_width=False,
                            cell_selectable=False,
                            style_table={"marginBotton": "1rem"}
                        )
                    ],
                    type="circle", color="#158cba"
                ),
                html.Br(),
                dbc.Row(
                    [
                        html.Div(
                            [
                                html.I(className="fa-solid fa-circle-info"),
                                html.P(
                                    '''offersIAP: Offers in-app purchases\
                                    \nRatingsStd: The standard deviation of user ratings\
                                    \nRatingsSkew: The skewness of user ratings (negative value - skewed towards positive ratings)\
                                    \ndescriptionSentiment: The app description's compound sentiment score, ranges from -1 to 1\
                                    \nreviewsSentiment: The average compound sentiment score of the reviews, ranges from -1 to 1\
                                    \ndescriptionReadability: The estimated school grade level required to understand the text\
                                    \ndescriptionGrammar: The grammatical correctness rate of the app description, up to 100\
                                    \nIAPMin: The minimum single-item price for in-app purchases\
                                    \nIAPMax: The maximum single-item price for in-app purchases\
                                    \ndeveloperCountry: The Alpha-2 (two-letter) code of the developer's country\
                                    \ndeveloperNApps: The number of unique apps the developer has on Play Store\
                                    \ndeveloperAppAgeMedian: The median age (years) of apps in the developer's portfolio''',
                                    className="info"
                                ),
                                " Glossary"
                            ],
                            className="tooltip"
                        ),
                    ]
                ),
                html.Br()
            ],
            width=6
        ),
        dbc.Col(
            [
                html.Br(),
                dcc.Loading(
                    [
                        dbc.Row(
                            [
                                dbc.Col(dcc.Graph(id="play-educational")),
                                dbc.Col(dcc.Graph(id="play-violent")),
                            ]
                        ),
                        dt.DataTable(
                            id='play-reviews'
                        )
                    ],
                    type="circle", color="#158cba"
                ),
            ],
            width=6
        )
    ],
    justify='center'
)

apple_tab = dbc.Row(
    [
        dbc.Col(
            dcc.Loading(
                dt.DataTable(
                    id='apple-details'
                ),
                type="circle", color="#158cba"
            ),
            width=6
        ),
        dbc.Col(
            dcc.Loading(
                dt.DataTable(
                    id='apple-reviews'
                ),
                type="circle", color="#158cba"
            ),
            width=6
        )
    ],
    justify='center'
) 


layout = dbc.Container(
    [
        html.Br(),
        search_bar,
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


# callback for updating search term when the search button is clicked
@dash.callback(
    Output('search-temp', 'data'),
    Input('search-button', 'n_clicks'),
    State('search-term', 'value')
)
def update_term(click, term):
    return term

# callbacks for updating metadata
@dash.callback(
    [
        Output('details-temp', 'data'),
        Output('reviews-temp', 'data')
    ],
    Input('search-type', 'value')
    Input('search-term', 'data')
)
def fetch_info(search_type, term):
    if "Play" in search_type:
        #app_id = term.split("play:")[1].strip()
        try:
            app = Play(app_id=app_id)
            play_details = app.get_details()
            play_reviews = app.get_reviews(sort='relevance')
        except:
            app = Play(search=app_id)
            play_details = app.get_details()
            play_reviews = app.get_reviews(sort='relevance')
    elif "Play" in search_type:
        #app_id = term.split("play:")[1].strip()
        pass
    else:
        app = Play(search=term)
        play_details = app.get_details()
        play_reviews = app.get_reviews(sort='relevance')
    return [play_details, play_reviews]

@dash.callback(
    [
        Output('play-title', 'children'),
        Output('play-title', 'href'),
        Output('play-id', 'children'),
        Output('play-img', 'src'),
    ],
    Input('details-temp', 'data')
)
def update_meta(data):
    return [data['title'], data['url'], data['appId'], data['icon']]

@dash.callback(
    [
        Output('play-details', 'data'),
        # Output('play-reviews', 'children'),
        # Output('apple-details', 'children'),
        # Output('apple-reviews', 'children')
    ],
    [
        Input('details-temp', 'data'),
        Input('reviews-temp', 'data')
    ],
    # background=True
)
def update_tables(details, reviews):
    play_info = play_features(details, reviews)
    filter_features = ['title', 'appId', 'description', 'inAppProductPrice', 'developerId',
                       'developerAddress', 'genre', 'contentRatingDescription', 'released']
    play_table = pd.DataFrame(play_info, index=[0])
    play_table.drop(columns=filter_features, inplace=True)
    return [play_table.melt(var_name="Feature", value_name="Value").to_dict('records')]

@dash.callback(
    [
        Output('play-educational', 'figure'),
        Output('play-violent', 'figure'),
    ],
    [
        Input('details-temp', 'data'),
        Input('reviews-temp', 'data')
    ]
)
def update_scores(details, reviews):
    play_info = play_features(details, reviews)
    pred_e = generate_predictions(play_info, 'educational')
    pred_v = generate_predictions(play_info, 'violent')
    fig_e = go.Figure(
        data=[
            go.Pie(
                values=[pred_e, 1-pred_e],
                hole=.3, hoverinfo="skip",
                marker_colors=['#158cba', '#d1d1d1'],
            )
        ], layout_showlegend=False)
    fig_e.update_layout(
        autosize=False,
        width=250,
        height=250,
        margin=dict(l=10, r=10, t=40, b=10),
        title_text="Educational",
        title_x=0.5,
        font_color="black",
    )
    fig_v = go.Figure(
        data=[
            go.Pie(
                values=[pred_v, 1-pred_v],
                hole=.3, hoverinfo="skip",
                marker_colors=['#158cba', '#d1d1d1'],
            )
        ], layout_showlegend=False)
    fig_v.update_layout(
        autosize=False,
        width=250,
        height=250,
        margin=dict(l=10, r=10, t=40, b=10),
        title_text="Violent",
        title_x=0.5,
        font_color="black",
    )
    return [fig_e, fig_v]