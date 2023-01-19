from dash import Dash, dcc, html, dash_table as dt
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from api import Play, Apple
from utils import *

THEME = dbc.themes.LUMEN

app = Dash(__name__, external_stylesheets=[THEME, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css"])
server = app.server
app.title = 'App Analyzer'

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
        html.Div(children="", id='search-temp', style={'display': 'none'}),
        html.Div(children=[], id='result-temp', style={'display': 'none'})
    ],
    class_name="g-0 ms-auto flex-wrap mt-3 mt-md-0",
    align="center",
    style={'min-width': '350px'}
)

header = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(src=app.get_asset_url('icon.png'), height="25px")
                        ),
                        dbc.Col(
                            dbc.NavbarBrand("App Analyzer", class_name="ms-2"),
                        ),
                    ],
                    align="center",
                    class_name="g-0",
                ),
                href="https://github.com/andy-techen/app-analyzer",
                style={"textDecoration": "none", 'fontWeight':'bold'},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                search_bar,
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ],
        class_name="mx-1",
        fluid=True
    ),
    color="dark",
    dark=True,
)

play_tab = dbc.Row(
    [
        dbc.Col(
            [
                html.Br(),
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
                dbc.Spinner(
                    dt.DataTable(
                        id='play-details',
                        columns=[
                            {"name": "Feature", "id": "Feature"},
                            {"name": "Value", "id": "Value"}
                        ],
                        style_as_list_view=True,
                        style_cell={'fontSize': 14, 'textAlign': 'left', 'paddingRight': '1rem'},
                        style_header={'fontWeight': 'bold', 'backgroundColor': '#999999', 'color': 'white'},
                        fill_width=False,
                        cell_selectable=False
                    )
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


body = dbc.Container(
    [
        html.Br(),
        dbc.Tabs(
            [
                dbc.Tab(play_tab, label="Play Store", tab_style={'marginLeft':'auto'}),
                dbc.Tab(apple_tab, label="Apple App Store")
            ]
        )
    ]
)


# callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# callback for updating search term when the search button is clicked
@app.callback(
    Output('search-temp', 'children'),
    [Input('search-button', 'n_clicks')],
    [State('search-term', 'value')]
)
def update_term(click, term):
    return term

# callbacks for updating metadata
@app.callback(
    [Output('result-temp', 'children')],
    [Input('search-temp', 'children')]
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

@app.callback(
    [
        Output('play-title', 'children'),
        Output('play-title', 'href'),
        Output('play-id', 'children'),
        Output('play-img', 'src'),
    ],
    [Input('result-temp', 'children')]
)
def update_meta(data):
    return [data['title'], data['url'], data['appId'], data['icon']]

@app.callback(
    [
        Output('play-details', 'data'),
        # Output('play-reviews', 'children'),
        # Output('apple-details', 'children'),
        # Output('apple-reviews', 'children')
    ],
    [Input('result-temp', 'children')]
)
def update_tables(data):
    play_table = play_features(data)
    return play_table


app.layout = html.Div([header, body])

if __name__ == '__main__':
    app.run_server(debug=True)