import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from api import Play, Apple

dash.register_page(__name__, path='/')






# APPLE TAB CONFIGURATION
apple_results = dbc.Row(
    [
        dbc.Col(
            [
                html.Br(),
                dcc.Loading(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(id='img-apple', height="55px"), width="auto", style={"margin": "auto"}
                                ),
                                dbc.Col(
                                    [
                                        html.H2(html.A(id='title-apple', target="_blank")),
                                        html.H6(["App ID: ", html.Span(id='id-apple')]),
                                    ]
                                )
                            ]
                        ),
                        dt.DataTable(
                            id='details-apple',
                            columns=[
                                {"name": "Feature", "id": "Feature"},
                                {"name": "Value", "id": "Value"}
                            ],
                            style_as_list_view=True,
                            style_cell={'fontSize': '1rem', 'textAlign': 'left', 'paddingRight': '2rem', 'fontFamily': "Helvetica Neue"},
                            style_header={'fontWeight': 'bold', 'backgroundColor': '#808080', 'color': 'white'},
                            fill_width=True,
                            cell_selectable=False,
                            style_table={"marginBotton": "1rem"}
                        )
                    ],
                    type="circle", color="#158cba"
                ),
                html.Br(),
            ],
            width=6
        ),
    ],
    justify='center'
)

apple_tab = dbc.Container(
    [
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(id="search-term-apple", type="search", placeholder="Enter an app ID such as '1024722275'", value="1024722275"),
                ),
                dbc.Col(
                    dbc.Button(
                        "Search", color="primary", class_name="ms-2",
                        id="search-button-apple", n_clicks=0
                    ),
                    width="auto",
                ),
            ]
        ),
        apple_results,
    ]
)






# GOOGLE PLAY TAB CONFIGURATION
play_results = dbc.Row(
    [
        dbc.Col(
            [
                html.Br(),
                dcc.Loading(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(id='img-play', height="55px"), width="auto", style={"margin": "auto"}
                                ),
                                dbc.Col(
                                    [
                                        html.H2(html.A(id='title-play', target="_blank")),
                                        html.H6(["App ID: ", html.Span(id='id-play')]),
                                    ]
                                )
                            ]
                        ),
                        dt.DataTable(
                            id='details-play',
                            columns=[
                                {"name": "Feature", "id": "Feature"},
                                {"name": "Value", "id": "Value"}
                            ],
                            style_as_list_view=True,
                            style_cell={'fontSize': '1rem', 'textAlign': 'left', 'paddingRight': '2rem', 'fontFamily': "Helvetica Neue"},
                            style_header={'fontWeight': 'bold', 'backgroundColor': '#808080', 'color': 'white'},
                            fill_width=True,
                            cell_selectable=False,
                            style_table={"marginBotton": "1rem"}
                        )
                    ],
                    type="circle", color="#158cba"
                ),
                html.Br(),
            ],
            width=6
        ),
        dbc.Col(
            dbc.Col(dcc.Graph(id="bar-play")),
            width=6
        )
    ],
    justify='center'
)

play_tab = dbc.Container(
    [
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(id="search-term-play", type="search", placeholder="Enter an app ID such as 'com.mojang.minecraftpe'", value="com.mojang.minecraftpe"),
                ),
                dbc.Col(
                    dbc.Button(
                        "Search", color="primary", class_name="ms-2",
                        id="search-button-play", n_clicks=0
                    ),
                    width="auto",
                ),
            ]
        ),
        play_results,
    ]
)





# PAGE LAYOUT
layout = dbc.Container(
    [
        html.Br(),
        dbc.Tabs(
            [
                dbc.Tab(apple_tab, label="Apple", tab_id='apple_tab', tab_style={'marginLeft':'auto'}),
                dbc.Tab(play_tab, label="Google Play", tab_id='play_tab'),
            ],
            active_tab="play_tab",
            id="tabs"
        )
    ]
)


@dash.callback(
    Output('search-button-apple', 'disabled'),
    Output('search-button-play', 'disabled'),
    Input('tabs', 'active_tab')
)
def disable_buttons(active_tab):
    apple_disabled = active_tab != 'apple_tab'
    play_disabled = active_tab != 'play_tab'
    return apple_disabled, play_disabled





########################################################################
# APPLE SCRAPER FUNCTIONS
@dash.callback(
    [
        Output('title-apple', 'children'),
        Output('title-apple', 'href'),
        Output('id-apple', 'children'),
        Output('img-apple', 'src'),
        Output('details-apple', 'data'),
    ],
    Input('search-button-apple', 'n_clicks'),
    State('search-term-apple', 'value'),
)
def apple_details(click, term):
    """
    Function to display details on Apple apps

    Parameters
    ----------
    term - (str) app id

    Returns
    -------
    List containing various information on the app scraped
    """
    try:
        app = Apple(app_id=term)
        apple_details = app.get_details()
    except Exception as e:
        print(e)
        return ["Error", "", "", "", []]

    ttii = [apple_details['trackName'], apple_details['trackViewUrl'], apple_details['trackId'], apple_details['artworkUrl100']]

    details = [
        {"Feature": "Content Rating", "Value": apple_details["contentAdvisoryRating"]},
        {"Feature": "Score", "Value": apple_details["averageUserRating"]},
        {"Feature": "# of Ratings", "Value": apple_details["userRatingCount"]},
        {"Feature": "Price", "Value": f"${apple_details['price']}"},
    ]
    return ttii + [details]









########################################################################
# GOOGLE PLAY SCRAPER FUNCTIONS
@dash.callback(
    [
        Output('title-play', 'children'),
        Output('title-play', 'href'),
        Output('id-play', 'children'),
        Output('img-play', 'src'),
        Output('details-play', 'data'),
        Output('bar-play', 'figure'),
    ],
    Input('search-button-play', 'n_clicks'),
    State('search-term-play', 'value'),
)
def play_details(click, term):
    """
    Function to display details on Google Play apps

    Parameters
    ----------
    term - (str) app id

    Returns
    -------
    List containing various information on the app scraped and a figure
    """
    try:
        app = Play(app_id=term)
        play_details = app.get_details()
    except Exception as e:
        print(e)
        return ["Error", "", "", "", []]


    ttii = [play_details['title'], play_details['url'], play_details['appId'], play_details['icon']]
    details = [
        {"Feature": "Content Rating", "Value": play_details["contentRating"]},
        {"Feature": "Score", "Value": play_details["score"]},
        {"Feature": "# of Ratings", "Value": play_details["ratings"]},
        {"Feature": "# of Reviews", "Value": play_details["reviews"]},
        {"Feature": "# of Installs", "Value": play_details["realInstalls"]},
        {"Feature": "Offers IAP?", "Value": play_details["offersIAP"]},
        {"Feature": "Ad Supported?", "Value": play_details["adSupported"]},
        {"Feature": "Price", "Value": f"${play_details['price']}"},
    ]


    star_ratings = [1, 2, 3, 4, 5]
    b = go.Figure(
        data=[
            go.Bar(
                x = star_ratings,
                y=play_details["histogram"],
            )
        ]
    )
    b.update_layout(
        title_text='Bar Chart of Play Details',
        xaxis_title='Value',
        yaxis_title='Frequency',
    )

    return ttii + [details, b]