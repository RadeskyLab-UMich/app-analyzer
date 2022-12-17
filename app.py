from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

THEME = dbc.themes.SLATE
DASH_CSS = "./styles.css"

app = Dash(__name__, external_stylesheets=[THEME, DASH_CSS])

if __name__ == '__main__':
    app.run_server(debug=True)