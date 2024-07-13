import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import api
from utils import *

dash.register_page(__name__)





search_bar = dbc.Row(
    [
        dbc.Col(
            dcc.Dropdown(["Play", "Apple"], value="Play", id='search-type')
        ),
        dbc.Col(
            dbc.Input(id="search-term", type="search", placeholder="Enter an App Name or Keywords", value="Minecraft Mojang"),
        ),
        dbc.Col(
            dbc.Button(
                "Search", color="primary", class_name="ms-2",
                id="search-button", n_clicks=0
            ),
            width="auto",
        ),
        dcc.Store(id='app-search', storage_type='session'),
        dcc.Store(id='app-details', storage_type='session'),
    ],
    class_name="g-0 ms-auto flex-wrap mx-auto",
    align="center",
    style={'width': '600px'}
)








apps = dbc.Row(
    [
        dbc.Col(
            [
                html.Br(),
                dcc.Loading(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(id='img1', height="55px"), width="auto", style={"margin": "auto"}
                                ),
                                dbc.Col(
                                    [
                                        html.H2(html.A(id='title1', target="_blank")),
                                        html.H6(["App ID: ", html.Span(id='id1')]),
                                    ]
                                )
                            ]
                        ),

                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(id='img2', height="55px"), width="auto", style={"margin": "auto"}
                                ),
                                dbc.Col(
                                    [
                                        html.H2(html.A(id='title2', target="_blank")),
                                        html.H6(["App ID: ", html.Span(id='id2')]),
                                    ]
                                )
                            ]
                        ),

                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(id='img3', height="55px"), width="auto", style={"margin": "auto"}
                                ),
                                dbc.Col(
                                    [
                                        html.H2(html.A(id='title3', target="_blank")),
                                        html.H6(["App ID: ", html.Span(id='id3')]),
                                    ]
                                )
                            ]
                        ),

                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(id='img4', height="55px"), width="auto", style={"margin": "auto"}
                                ),
                                dbc.Col(
                                    [
                                        html.H2(html.A(id='title4', target="_blank")),
                                        html.H6(["App ID: ", html.Span(id='id4')]),
                                    ]
                                )
                            ]
                        ),

                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(id='img5', height="55px"), width="auto", style={"margin": "auto"}
                                ),
                                dbc.Col(
                                    [
                                        html.H2(html.A(id='title5', target="_blank")),
                                        html.H6(["App ID: ", html.Span(id='id5')]),
                                    ]
                                )
                            ]
                        ),

                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(id='img6', height="55px"), width="auto", style={"margin": "auto"}
                                ),
                                dbc.Col(
                                    [
                                        html.H2(html.A(id='title6', target="_blank")),
                                        html.H6(["App ID: ", html.Span(id='id6')]),
                                    ]
                                )
                            ]
                        ),

                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(id='img7', height="55px"), width="auto", style={"margin": "auto"}
                                ),
                                dbc.Col(
                                    [
                                        html.H2(html.A(id='title7', target="_blank")),
                                        html.H6(["App ID: ", html.Span(id='id7')]),
                                    ]
                                )
                            ]
                        ),

                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(id='img8', height="55px"), width="auto", style={"margin": "auto"}
                                ),
                                dbc.Col(
                                    [
                                        html.H2(html.A(id='title8', target="_blank")),
                                        html.H6(["App ID: ", html.Span(id='id8')]),
                                    ]
                                )
                            ]
                        ),

                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(id='img9', height="55px"), width="auto", style={"margin": "auto"}
                                ),
                                dbc.Col(
                                    [
                                        html.H2(html.A(id='title9', target="_blank")),
                                        html.H6(["App ID: ", html.Span(id='id9')]),
                                    ]
                                )
                            ]
                        ),

                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(id='img10', height="55px"), width="auto", style={"margin": "auto"}
                                ),
                                dbc.Col(
                                    [
                                        html.H2(html.A(id='title10', target="_blank")),
                                        html.H6(["App ID: ", html.Span(id='id10')]),
                                    ]
                                )
                            ]
                        ),
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




### LAYOUT
layout = dbc.Container(
    [
        html.Br(),
        search_bar,
        html.Br(),
        apps
    ]
)











### FUNCTIONS
@dash.callback(
    Output('app-details', 'data'),
    Input('search-button', 'n_clicks'),
    State('search-term', 'value'),
    State('search-type', 'value')
)
def fetch_info(click, term, search_type):
    """
    Function to search for the data based on the search term provided.

    Parameters
    ----------
    term (str) - search term entered by user
    search_type (str) - selection of App Store to search

    Returns
    -------
    apps (list) - list of apps with four basic identifiers: title, url, ID, and icon
    """

    if "Play" in search_type:
        try:
            app = api.search_app(term, store='play', strategy=10)
            apps = [{"title": id["title"], "url": "https://play.google.com/store/apps/details?id="+id["appId"], "appId": id["appId"], "icon": id["icon"]} for id in app]

            return apps
        except Exception as e:
            print(f"Exception occurred: {e}")
    elif "Apple" in search_type:
        try:
            app = api.search_app(term, store='apple', strategy=10)
            app = [Apple(app_id=id).get_details() for id in app]

            apps = [{"title": id["trackName"], "url": id["trackViewUrl"], "appId": id["trackId"], "icon": id["artworkUrl100"]} for id in app]

            return apps
        except Exception as e:
            print(f"Exception occurred: {e}")

@dash.callback(
    [
        Output('title1', 'children'),
        Output('title1', 'href'),
        Output('id1', 'children'),
        Output('img1', 'src'),

        Output('title2', 'children'),
        Output('title2', 'href'),
        Output('id2', 'children'),
        Output('img2', 'src'),

        Output('title3', 'children'),
        Output('title3', 'href'),
        Output('id3', 'children'),
        Output('img3', 'src'),

        Output('title4', 'children'),
        Output('title4', 'href'),
        Output('id4', 'children'),
        Output('img4', 'src'),

        Output('title5', 'children'),
        Output('title5', 'href'),
        Output('id5', 'children'),
        Output('img5', 'src'),

        Output('title6', 'children'),
        Output('title6', 'href'),
        Output('id6', 'children'),
        Output('img6', 'src'),

        Output('title7', 'children'),
        Output('title7', 'href'),
        Output('id7', 'children'),
        Output('img7', 'src'),

        Output('title8', 'children'),
        Output('title8', 'href'),
        Output('id8', 'children'),
        Output('img8', 'src'),

        Output('title9', 'children'),
        Output('title9', 'href'),
        Output('id9', 'children'),
        Output('img9', 'src'),

        Output('title10', 'children'),
        Output('title10', 'href'),
        Output('id10', 'children'),
        Output('img10', 'src'),
    ],
    Input('app-details', 'data')
)
def update_meta(data):
    """
    Function to display the data gathered based on the search.

    Parameters
    ----------
    data (list) - list of dictionaries for each app

    Returns
    -------
    Each element of each dictionary in the list
    """

    return [data[0]['title'], data[0]['url'], data[0]['appId'], data[0]['icon'],
        data[1]['title'], data[1]['url'], data[1]['appId'], data[1]['icon'],
        data[2]['title'], data[2]['url'], data[2]['appId'], data[2]['icon'],
        data[3]['title'], data[3]['url'], data[3]['appId'], data[3]['icon'],
        data[4]['title'], data[4]['url'], data[4]['appId'], data[4]['icon'],
        data[5]['title'], data[5]['url'], data[5]['appId'], data[5]['icon'],
        data[6]['title'], data[6]['url'], data[6]['appId'], data[6]['icon'],
        data[7]['title'], data[7]['url'], data[7]['appId'], data[7]['icon'],
        data[8]['title'], data[8]['url'], data[8]['appId'], data[8]['icon'],
        data[9]['title'], data[9]['url'], data[9]['appId'], data[9]['icon'],]


