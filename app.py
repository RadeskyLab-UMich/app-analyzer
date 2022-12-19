from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

THEME = dbc.themes.LUMEN
STATIC = "./static/"

app = Dash(__name__, external_stylesheets=[THEME, STATIC + 'styles.css'])

search_bar = dbc.Row(
    [
        dbc.Col(
            dbc.Input(type="search", placeholder="Enter an app ID or keywords"),
        ),
        dbc.Col(
            dbc.Button(
                "Search", color="primary", class_name="ms-2", n_clicks=0
            ),
            width="auto",
        ),
    ],
    class_name="g-0 ms-auto flex-wrap mt-3 mt-md-0",
    align="center",
    style={'min-width': '350px'}
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(src=STATIC + 'icon.png', height="25px")
                        ),
                        dbc.Col(
                            dbc.NavbarBrand("App Analyzer", className="ms-2"),
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


# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


app.layout = html.Div([navbar])

if __name__ == '__main__':
    app.run_server(debug=True)