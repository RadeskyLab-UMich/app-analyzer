import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import time
from datetime import datetime
import asyncio
import io
import random
import pandas as pd

from api import Play, Apple
from apple_scraper import AppleApp
from amazon_scraper import AmazonApp
from play_scraper import GoogleApp
from youtube_scraper import *


dash.register_page(__name__)






# AMAZON TAB CONFIGURATION
amazon_tab = dbc.Container(
    [
        html.Br(),
        dbc.Textarea(
            className="mb-3", style={"height": "20rem"}, id="dl-input-amazon",
            placeholder="Enter the app package names or ASINs for the app features you wish to download. Please place one app per line.\nEx:\nB07DXGT5C4\norg.pbskids.video\nB0C14XRMNM\ncom.learninga_z.onyourown"
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    dbc.Button("Download", color="primary", id="confirm-button-amazon", n_clicks=0),
                    dcc.Download(id="dl-amazon")
                    ],
                    width="auto"
                ),
                dbc.Col(
                    dbc.Progress(id="dl-amazon-progress", style={"height": "2rem"}, animated=True, striped=True),
                    width=3
                ),
            ],
            class_name="g-1"
        ),
    ]
)

# APPLE TAB CONFIGURATION
apple_tab = dbc.Container(
    [
        html.Br(),
        dbc.Textarea(
            className="mb-3", style={"height": "20rem"}, id="dl-input-apple",
            placeholder="Enter the app IDs for the app features you wish to download. Please place one app per line.\nEx:\n1024722275\n1448010566"
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    dbc.Button("Download", color="primary", id="confirm-button-apple", n_clicks=0),
                    dcc.Download(id="dl-apple")
                    ],
                    width="auto"
                ),
                dbc.Col(
                    dbc.Progress(id="dl-apple-progress", style={"height": "2rem"}, animated=True, striped=True),
                    width=3
                ),
            ],
            class_name="g-1"
        ),
    ]
)

# GOOGLE PLAY TAB CONFIGURATION
play_tab = dbc.Container(
    [
        html.Br(),
        dbc.Textarea(
            className="mb-3", style={"height": "20rem"}, id="dl-input-play",
            placeholder="Enter the app IDs for the app features you wish to download. Please place one app per line.\nEx:\ncom.duolingo\nvitaminshoppe.consumerapp"
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button("Download", color="primary", id="confirm-button-play", n_clicks=0),
                        dcc.Download(id="dl-play")
                    ],
                    width="auto"
                ),
                dbc.Col(
                    dbc.Progress(id="dl-play-progress", style={"height": "2rem"}, animated=True, striped=True),
                    width=3
                ),
            ],
            class_name="g-2",
            align='center'
        ),
    ]
)

# YOUTUBE TAB CONFIGURATION
you_tab = dbc.Container(
    [
        html.Br(),
        dbc.Textarea(
            className="mb-3", style={"height": "20rem"}, id="dl-input-you",
            placeholder="Enter the video IDs for the YouTube features you wish to download. Please place one video per line.\nEx:\n_cVGrRNi_2k\nSGM--zQnCME"
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button("Download", color="primary", id="confirm-button-you", n_clicks=0),
                    # dcc.Download(id="dl-you"),
                    width="auto"
                ),
                dbc.Col(
                    dcc.Loading(id="loading-you", type="circle", children=[dcc.Download(id='dl-you')]),
                    width=3
                )
            ],
            class_name="g-2",
            align='center'
        ),
    ]
)


# PAGE LAYOUT
layout = dbc.Container(
    [
        html.Br(),
        dbc.Tabs(
            [
                dbc.Tab(amazon_tab, label="Amazon", tab_id="amazon_tab", tab_style={'marginLeft':'auto'}),
                dbc.Tab(apple_tab, label="Apple", tab_id='apple_tab'),
                dbc.Tab(play_tab, label="Google Play", tab_id='play_tab'),
                dbc.Tab(you_tab, label="YouTube", tab_id="you_tab"),
            ],
            active_tab="play_tab",
        )
    ]
)







def get_excel(df, df2, filename):
    """
    Function to turn dataframes into an excel workbook

    Parameters
    ----------
    df - Pandas Dataframe
    df2 - Pandas dataframe
    filename (str) - filename to give to excel file

    Returns
    -------
    Download of the excel file
    """
    with io.BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='apps_found', index=False)
            df2.to_excel(writer, sheet_name='not_found', index=False)

            workbook  = writer.book
            worksheet1 = writer.sheets['apps_found']
            worksheet2 = writer.sheets['not_found']

            wrap_format = workbook.add_format({'text_wrap': True})

            row_format = workbook.add_format()
            row_format.set_text_wrap(True)
            row_height = 100

            for row_num in range(1, len(df) + 1):
                worksheet1.set_row(row_num, row_height, wrap_format)

        buffer.seek(0)
        return dcc.send_bytes(buffer.getvalue(), filename)






def scrape(set_progress, apps_ls, n_apps, time_sleep, app_class):
    """
    Function to scrape data for the Amazon, Apple, and Google Play scrapers

    Parameters
    ----------
    apps_ls (list) - list of app_ids
    n_apps (int) - number of apps in list
    time_sleep (list) - list of two numbers used for random to get seconds to delay between apps scraped
    app_class (str) - text identifying which scraper to use (ex: 'amazon')

    Returns
    -------
    full_apps_ls - list of dictionaries of the scraped apps
    not_found2 - list of app_ids not found
    """
    full_apps_ls = []
    not_found = []
    not_found2 = []

    for idx, app_id in enumerate(apps_ls):
        print(f"Fetching {idx + 1}/{n_apps}: {app_id}")
        set_progress((idx + 1, f"{int((idx + 1) / n_apps * 100)} %", n_apps))
        app_found = False

        try:
            if app_class == "amazon":
                app_info = AmazonApp(id=app_id.strip())
                amazon_details = app_info.get_app()

                if amazon_details == {}:
                    not_found.append(app_id)
                else:
                    full_apps_ls.append(amazon_details)
            elif app_class == "apple":
                app_info = Apple(app_id=app_id.strip())
                apple_details = app_info.get_details()
                app_found = True
            else:
                app_info = Play(app_id=app_id.strip())
                play_info = app_info.get_details()
                app_found = True


            if app_found:
                check = False
                count = 0

                while check == False and count < 30:
                    try:
                        if app_class == "apple":
                            app = AppleApp(id=f"{app_id}")
                            apple_details2 = app.get_app()

                            if apple_details2:
                                apple_details.update(apple_details2)
                                full_apps_ls.append(apple_details)
                                check = True
                        else:
                            app = GoogleApp(app_id)
                            play_info2 = app.get_app()

                            if play_info2:
                                play_info.update(play_info2)
                                full_apps_ls.append(play_info)
                                check = True
                    except Exception as e:
                        print(e)

                    count += 1
                    time.sleep(1)

                if count == 30:
                    full_apps_ls.append(apple_details)


            time.sleep(random.randint(time_sleep[0], time_sleep[1]))
        except Exception as e:
            print(e)
            not_found.append(app_id)

        time.sleep(random.randint(time_sleep[0], time_sleep[1]))

    for app_id in not_found:
        try:
            if app_class == "amazon":
                app_info = AmazonApp(id=app_id.strip())
                amazon_details = app_info.get_app()

                if amazon_details == {}:
                    not_found2.append(app_id)
                else:
                    full_apps_ls.append(amazon_details)
            elif app_class == "apple":
                app_info = Apple(app_id=app_id.strip())
                apple_details = app_info.get_details()
                app_found = True
            else:
                app_info = Play(app_id=app_id.strip())
                play_info = app_info.get_details()
                app_found = True


            if app_found:
                check = False
                count = 0

                while check == False and count < 30:
                    try:
                        if app_class == "apple":
                            app = AppleApp(id=f"{app_id}")
                            apple_details2 = app.get_app()

                            if apple_details2:
                                apple_details.update(apple_details2)
                                full_apps_ls.append(apple_details)
                                check = True
                        else:
                            app = GoogleApp(app_id)
                            play_info2 = app.get_app()

                            if play_info2:
                                play_info.update(play_info2)
                                full_apps_ls.append(play_info)
                                check = True
                    except Exception as e:
                        print(e)

                    count += 1
                    time.sleep(1)

                if count == 30:
                    full_apps_ls.append(apple_details)

            time.sleep(random.randint(time_sleep[0], time_sleep[1]))
        except Exception as e:
            print(e)
            not_found2.append(app_id)

        time.sleep(random.randint(time_sleep[0], time_sleep[1]))

    return full_apps_ls, not_found2






########################################################################
# AMAZON SCRAPER FUNCTIONS
@dash.callback(
    Output('dl-amazon', 'data'),
    [
        Input('confirm-button-amazon', 'n_clicks'),
    ],
    [
        State('dl-input-amazon', 'value'),
    ],
    running=[
        (Output("dl-amazon-progress", "animated"), True, False),
    ],
    progress=[
        Output("dl-amazon-progress", "value"),
        Output("dl-amazon-progress", "label"),
        Output("dl-amazon-progress", "max")
    ],
    prevent_initial_call=True,
    background=True
)
def update_amazon_info(set_progress, click, apps):
    """
    Function to scrape data on Apple iTunes store items such as apps and download them in an .xlsx file.

    Parameters
    ----------
    apps (str) - string of app/song/etc. IDs

    Returns
    -------
    df (download) - dataframe of the scraped ID information
    """
    apps_ls = apps.split('\n')
    n_apps = len(apps_ls)
    full_amazon_ls, not_found = scrape(set_progress, apps_ls, n_apps, [60, 100], "amazon")

    df = pd.DataFrame(full_amazon_ls)
    df2 = pd.DataFrame({"appId": not_found})

    return get_excel(df, df2, "amazon_features.xlsx")







########################################################################
# APPLE SCRAPER FUNCTIONS
@dash.callback(
    Output('dl-apple', 'data'),
    [
        Input('confirm-button-apple', 'n_clicks'),
    ],
    [
        State('dl-input-apple', 'value'),
    ],
    running=[
        (Output("dl-apple-progress", "animated"), True, False),
    ],
    progress=[
        Output("dl-apple-progress", "value"),
        Output("dl-apple-progress", "label"),
        Output("dl-apple-progress", "max")
    ],
    prevent_initial_call=True,
    background=True
)
def update_apple_info(set_progress, click, apps):
    """
    Function to scrape data on Apple iTunes store items such as apps and download them in an .xlsx file.

    Parameters
    ----------
    apps (str) - string of app/song/etc. IDs

    Returns
    -------
    df (download) - dataframe of the scraped ID information
    """
    apps_ls = apps.split('\n')
    n_apps = len(apps_ls)
    full_apple_ls, not_found = scrape(set_progress, apps_ls, n_apps, [1, 2], "apple")

    df = pd.DataFrame(full_apple_ls)

    if "ipadScreenshotUrls" in df:
        df.drop(columns=["ipadScreenshotUrls"], inplace=True)
    if "appletvScreenshotUrls" in df:
        df.drop(columns=["appletvScreenshotUrls"], inplace=True)
    if "artworkUrl60" in df:
        df.drop(columns=["artworkUrl60"], inplace=True)
    if "artworkUrl512" in df:
        df.drop(columns=["artworkUrl512"], inplace=True)
    if "artworkUrl100" in df:
        df.drop(columns=["artworkUrl100"], inplace=True)
    if "screenshotUrls" in df:
        df.drop(columns=["screenshotUrls"], inplace=True)
    if "artistViewUrl" in df:
        df.drop(columns=["artistViewUrl"], inplace=True)
    if "sellerUrl" in df:
        df.drop(columns=["sellerUrl"], inplace=True)
    if "sellerUrl" in df:
        df.drop(columns=["sellerUrl"], inplace=True)

    today = datetime.now()
    formatted_date = today.strftime("%m/%d/%Y")
    df["date_scraped"] = formatted_date

    first_column = df.pop('date_scraped')
    df.insert(0, 'date_scraped', first_column)

    df2 = pd.DataFrame({"appId": not_found})

    return get_excel(df, df2, "apple_features.xlsx")





########################################################################
# GOOGLE PLAY SCRAPER FUNCTIONS
@dash.callback(
    Output('dl-play', 'data'),
    [
        Input('confirm-button-play', 'n_clicks'),
    ],
    [
        State('dl-input-play', 'value'),
    ],
    running=[
        (Output("dl-play-progress", "animated"), True, False),
    ],
    progress=[
        Output("dl-play-progress", "value"),
        Output("dl-play-progress", "label"),
        Output("dl-play-progress", "max")
    ],
    prevent_initial_call=True,
    background=True
)
def update_play_info(set_progress, click, apps):
    """
    Function to scrape data on Google Play apps and download them in an .xlsx file.

    Parameters
    ----------
    apps (str) - string of video IDs

    Returns
    -------
    df (download) - dataframe of the scraped app ID information
    """
    apps_ls = apps.split('\n')
    n_apps = len(apps_ls)
    full_play_ls, not_found = scrape(set_progress, apps_ls, n_apps, [1, 2], "google")


    df = pd.DataFrame(full_play_ls)
    if "icon" in df:
        df.drop(columns=["icon"], inplace=True)
    if "headerImage" in df:
        df.drop(columns=["headerImage"], inplace=True)
    if "screenshots" in df:
        df.drop(columns=["screenshots"], inplace=True)
    if "video" in df:
        df.drop(columns=["video"], inplace=True)
    if "videoImage" in df:
        df.drop(columns=["videoImage"], inplace=True)
    if "descriptionHTML" in df:
        df.drop(columns=["descriptionHTML"], inplace=True)
    if "developerWebsite" in df:
        df.drop(columns=["developerWebsite"], inplace=True)
    if "privacyPolicy" in df:
        df.drop(columns=["privacyPolicy"], inplace=True)

    today = datetime.now()
    formatted_date = today.strftime("%m/%d/%Y")
    df["date_scraped"] = formatted_date

    first_column = df.pop('date_scraped')
    df.insert(0, 'date_scraped', first_column)


    df2 = pd.DataFrame({"appId": not_found})

    return get_excel(df, df2, "play_features.xlsx")









########################################################################
# YOUTUBE SCRAPER FUNCTIONS
async def get_videos(click, vids):
    """
    Function to get video details based on the list provided.

    Parameters
    ----------
    vids (str) - video IDs

    Returns
    -------
    video_df - pandas DataFrame of thevideo details

    """
    video_ids = vids.split()
    scraper = YoutubeScraper()

    tasks = [scraper.get_video_page(video_id) for video_id in video_ids]
    responses = dict(await asyncio.gather(*tasks))

    rows = [scraper.get_video(video_id, response) for video_id, response in responses.items()]
    video_df = pd.DataFrame(rows).replace(r'^\s*$', None, regex=True)

    # video_df = await scraper.get_video_metadata(video_ids)
    await scraper.close_session()

    return video_df




@dash.callback(
    Output('dl-you', 'data'),
    [
        Input('confirm-button-you', 'n_clicks'),
    ],
    [
        State('dl-input-you', 'value'),
    ],
    prevent_initial_call=True,
    background=True
)
def update_youtube_info(click, vids):
    """
    Function to scrape data on YouTube videos and download them in an .xlsx file.

    Parameters
    ----------
    vids (str) - string of video IDs

    Returns
    -------
    df (download) - dataframe of the scraped video ID information
    """

    df = asyncio.run(get_videos(click, vids))

    today = datetime.now()
    formatted_date = today.strftime("%m/%d/%Y")
    df["date_scraped"] = formatted_date

    first_column = df.pop('date_scraped')
    df.insert(0, 'date_scraped', first_column)
    return dcc.send_data_frame(df.to_excel, "youtube_features.xlsx", index=False)