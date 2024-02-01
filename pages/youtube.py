import time
import asyncio
import pandas as pd
import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash.dependencies import Input, Output, State
from youtube_scraper import *

dash.register_page(__name__)

youtube_search = dbc.Container(
    [
        html.Br(),
        dbc.Textarea(
            className="mb-3", style={"height": "20rem"}, id="dl-input-you",
            placeholder="Enter the video IDs for the YouTube features you wish to download. Please place one video per line."
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button("Confirm", color="primary", id="confirm-button-you", n_clicks=0),
                    width="auto"
                ),
                dbc.Col(
                    [
                        dbc.Button("Download as CSV", color="secondary", id="dl-button-you", n_clicks=0, disabled=True),
                        dcc.Download(id="dl-you")
                    ],
                    width="auto"
                ),
                # dbc.Col(
                #     dbc.Progress(id="dl-you-progress", style={"height": "2rem"}, animated=True, striped=True),
                #     width=3
                # )
            ],
            class_name="g-2",
            align='center'
        ),
        dcc.Store(id="dl-temp-you", storage_type='session')
    ]
)

layout = dbc.Container(
    [
        html.Br(),
        youtube_search
    ]
)



async def get_videos(click, apps):
    """
    Function to get video details based on the list provided
    Parameters
    ----------
    click - action
    apps (list) - video IDs

    Returns
    -------
    list - video details

    """
    scraper = YoutubeScraper()

    video_ids = apps.split()
    video_df = await scraper.video_metadata(video_ids)

    return video_df




@dash.callback(
    Output('dl-temp-you', 'data'),
    [
        Input('confirm-button-you', 'n_clicks'),
    ],
    [
        State('dl-input-you', 'value'),
    ],
    running=[
        (Output("dl-button-you", "disabled"), True, False),
        #(Output("dl-button-you", "color"), "green"),
        #(Output("dl-you-progress", "animated"), True, False),
    ],
    # progress=[
    #     Output("dl-you-progress", "value"),
    #     Output("dl-you-progress", "label"),
    #     Output("dl-you-progress", "max")
    # ],
    prevent_initial_call=True,
    background=True
)
def get_vids(click, apps):
    """
    Function to
    Parameters
    ----------
    click - action
    apps (list) - list of video IDs

    Returns
    -------
    dict - dictionary of video IDs and their details
    """
    return asyncio.run(get_videos(click, apps)).to_dict()



@dash.callback(
    Output('dl-you', 'data'),
    Input('dl-button-you', 'n_clicks'),
    [
        State('dl-temp-you', 'data'),
    ],
    prevent_initial_call=True
)
def download_vid_info(click, data):
    """
    Function to
    Parameters
    ----------
    click
    data (dict) - dictionary of video IDs and their details

    Returns
    -------
    download - csv of the video IDs and their details
    """
    #print(data)
    df = pd.DataFrame(data)
    #print()
    #print(df)
    return dcc.send_data_frame(df.to_csv, "youtube_vids.csv", index=False)
