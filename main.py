from dash import DiskcacheManager, Dash, dcc, html, dash_table as dt, page_registry, page_container
import dash_bootstrap_components as dbc

import diskcache
cache = diskcache.Cache("./tmp")
bcm = DiskcacheManager(cache)

THEME = dbc.themes.LUMEN

app = Dash(
    __name__,
    external_stylesheets=[THEME, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css"],
    use_pages=True, 
    background_callback_manager=bcm
)
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
                        )
                    ],
                    align="center",
                    class_name="g-0",
                ),
                href=page_registry['pages.home']['path'],
                style={"textDecoration": "none", 'fontWeight':'bold'},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Link('Download', href=page_registry['pages.download']['path']),
                        width="auto",
                        className="nav-link"
                    ),
                    dbc.Col(
                        dcc.Link('YouTube', href=page_registry['pages.youtube']['path']),
                        width="auto",
                        className="nav-link"
                    ),
                    dbc.Col(
                        html.A('Code', href="https://github.com/andy-techen/app-analyzer", target="_blank"),
                        width="auto",
                        className="nav-link"
                    ),
                    dbc.Col(
                        html.A('Docs', href="https://www.dropbox.com/scl/fi/trner1899b1dk09o1e1ch/App-Data-Analyzer-Documentation.paper?dl=0&rlkey=1qyxf866ivofi6we0fu96ej9s", target="_blank"),
                        width="auto",
                        className="nav-link"
                    )
                ],
                className="g-0",
            )
        ],
        class_name="mx-1",
        fluid=True
    ),
    color="dark",
    dark=True,
)

app.layout = html.Div([header, page_container])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080, threaded=True)