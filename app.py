import dash
from dash import Dash, dcc, html, dash_table as dt
import dash_bootstrap_components as dbc

THEME = dbc.themes.LUMEN

app = Dash(__name__, external_stylesheets=[THEME, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css"], use_pages=True)
server = app.server
app.title = 'App Analyzer'

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
                href="https://app-analyzer.onrender.com/",
                style={"textDecoration": "none", 'fontWeight':'bold'},
            ),
        ],
        class_name="mx-1",
        fluid=True
    ),
    color="dark",
    dark=True,
)

app.layout = html.Div([header, dash.page_container])

if __name__ == '__main__':
    app.run_server(debug=True)