import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from api import Play, Apple
from utils import *

dash.register_page(__name__, path='/')

search_bar = dbc.Row(
    [
        dbc.Col(
            html.Abbr(
                html.I(className="fa-solid fa-circle-info"),
                title='''Search with Play Store app ID - play: <id>\
                    \nSearch with App Store app title - apple: <title>\
                    \nSearch with keywords - <keywords>'''
            ),
            width=1
        ),
        dbc.Col(
            dbc.Input(id="search-term", type="search", placeholder="Enter an app ID or keywords", value="play: com.mojang.minecraftpe"),
        ),
        dbc.Col(
            dbc.Button(
                "Search", color="primary", class_name="ms-2",
                id="search-button", n_clicks=0
            ),
            width="auto",
        ),
        dcc.Store(id='search-temp'),
        dcc.Store(id='result-temp')
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
                dbc.Spinner(
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
                            style_cell={'fontSize': 14, 'textAlign': 'left', 'paddingRight': '2rem', 'fontFamily': "Helvetica Neue"},
                            style_header={'fontWeight': 'bold', 'backgroundColor': '#999999', 'color': 'white'},
                            fill_width=False,
                            cell_selectable=False
                        )
                    ]
                )
            ],
            width=6
        ),
        dbc.Col(
            dbc.Spinner(
                dt.DataTable(
                    id='play-reviews'
                )
            ),
            width=6
        )
    ],
    justify='center'
)

apple_tab = dbc.Row(
    [
        dbc.Col(
            dbc.Spinner(
                dt.DataTable(
                    id='apple-details'
                )
            ),
            width=6
        ),
        dbc.Col(
            dbc.Spinner(
                dt.DataTable(
                    id='apple-reviews'
                )
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
                dbc.Tab(apple_tab, label="Apple App Store", tab_id='apple_tab')
            ],
            active_tab="play_tab",
        )
    ]
)


# callback for updating search term when the search button is clicked
@dash.callback(
    Output('search-temp', 'data'),
    [Input('search-button', 'n_clicks')],
    [State('search-term', 'value')]
)
def update_term(click, term):
    return term

# callbacks for updating metadata
@dash.callback(
    [Output('result-temp', 'data')],
    [Input('search-temp', 'data')]
)
def fetch_details(term):
    if "play: " in term:
        app_id = term.split("play:")[1].strip()
        app = Play(app_id=app_id)
        play_details = app.get_details()
    elif "apple: " in term:
        app_id = term.split("play:")[1].strip()
    else:
        app = Play(search=term)
        play_details = app.get_details()
    return [play_details]

@dash.callback(
    [
        Output('play-title', 'children'),
        Output('play-title', 'href'),
        Output('play-id', 'children'),
        Output('play-img', 'src'),
    ],
    [Input('result-temp', 'data')]
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
    [Input('result-temp', 'data')]
)
def update_tables(data):
    play_table = play_features(data)
    return play_table