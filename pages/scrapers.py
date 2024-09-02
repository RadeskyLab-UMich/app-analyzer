import time
import asyncio
import dash
from dash import html, dcc, dash_table as dt
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash.dependencies import Input, Output, State
from api import Play, Apple
from utils import *
from youtube_scraper import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import language_tool_python
from apple_scraper import AppleApp
from play_scraper import GoogleApp
import io
from datetime import datetime

dash.register_page(__name__)






features_derived_play = ['ratingsStd', 'ratingsSkew', 'descriptionSentiment', 'reviewsSentiment', 'descriptionReadability', 'descriptionGrammar',
'developerNApps', 'developerAppAgeMedian', 'developerCountry', 'releasedYear']

features_derived_apple = ['ratingsStd', 'ratingsSkew', 'descriptionSentiment', 'reviewsSentiment', 'descriptionReadability', 'descriptionGrammar',
'developerNApps', 'developerAppAgeMedian', 'developerCountry', 'releasedYear']

features_tube = ['video_id', 'unavailable', 'private', 'requires_payment', 'is_livestream_recording_not_available', 'livestream_recording_not_available',
            'title', 'description', 'view_count', 'length_seconds', 'channel_name', 'channel_id', 'channel_url', 'family_safe', 'unlisted', 'live_content',
            'removed', 'category', 'upload_date', 'publish_date', 'video_recommendations']


# GOOGLE PLAY TAB CONFIGURATION
play_tab = dbc.Container(
    [
        html.Br(),
        dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(sorted(features_derived_play), persistence=True, multi=True, placeholder="Select Derived Features", id="filters-derived-play")
            ),
            dbc.Col(dmc.Checkbox(id="predict-checkbox", label="Include Predictions"), width="auto")
        ],
        class_name="g-2 ms-auto flex-wrap mx-auto",
        align="center",
        style={"width": "1000px"}
        ),
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

# APPLE TAB CONFIGURATION
apple_tab = dbc.Container(
    [
        html.Br(),
        # dbc.Row(
        # [
        #     dbc.Col(
        #         dcc.Dropdown(sorted(features_derived_apple), persistence=True, multi=True, placeholder="Select Derived Features", id="filters-derived-apple")
        #     ),
        #     # dbc.Col(dmc.Checkbox(id="predict-checkbox", label="Include Predictions"), width="auto")
        # ],
        # class_name="g-2 ms-auto flex-wrap mx-auto",
        # align="center",
        # style={"width": "1000px"}
        # ),
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

# YOUTUBE TAB CONFIGURATION
you_tab = dbc.Container(
    [
        html.Br(),
        dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(sorted(features_tube), value=['title', 'video_id'], persistence=True, multi=True, placeholder="Select Features", id="you-filters")
            ),
        ],
        class_name="g-2 ms-auto flex-wrap mx-auto",
        align="center",
        style={"width": "1000px"}
        ),
        html.Br(),
        dbc.Textarea(
            className="mb-3", style={"height": "20rem"}, id="dl-input-you",
            placeholder="Enter the video IDs for the YouTube features you wish to download. Please place one video per line.\nEx:\n_cVGrRNi_2k\nSGM--zQnCME"
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    dbc.Button("Download", color="primary", id="confirm-button-you", n_clicks=0),
                    dcc.Download(id="dl-you")
                    ],
                    width="auto"
                ),
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
                dbc.Tab(apple_tab, label="Apple", tab_id='apple_tab', tab_style={'marginLeft':'auto'}),
                dbc.Tab(play_tab, label="Google Play", tab_id='play_tab'),
                dbc.Tab(you_tab, label="YouTube", tab_id="you_tab")
            ],
            active_tab="play_tab",
        )
    ]
)









########################################################################
# GOOGLE PLAY SCRAPER FUNCTIONS
@dash.callback(
    Output('dl-play', 'data'),
    # Output('dl-temp-play', 'data'),
    # Output('dl-temp-play-none', 'data'),
    [
        Input('confirm-button-play', 'n_clicks'),
    ],
    [
        State('predict-checkbox', 'checked'),
        State('dl-input-play', 'value'),
        # State('filters-base', 'value'), # added
        State('filters-derived-play', 'value') # added
    ],
    running=[
        # (Output("dl-button-play", "disabled"), True, False),
        # (Output("dl-button-play2", "disabled"), True, False),
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
def update_play_info(set_progress, click, predict, apps, derived): # , base):
    """
    Function to scrape data on Google Play apps and download them in an .xlsx file.

    Parameters
    ----------
    apps (str) - string of video IDs

    Returns
    -------
    df (download) - dataframe of the scraped app ID information
    """

    full_play_ls = []
    not_found = []
    not_found2 = []
    apps_ls = apps.split('\n')
    n_apps = len(apps_ls)

    if derived:
        if "descriptionGrammar" in derived:
            tool = language_tool_python.LanguageTool('en-US')
            # tool = language_tool_python.LanguageToolPublicAPI('en-US') # use this if running the webapp locally

    for idx, app_id in enumerate(apps_ls):
        print(f"Fetching {idx + 1}/{n_apps}: {app_id}")
        set_progress((idx + 1, f"{int((idx + 1) / n_apps * 100)} %", n_apps))
        app_found = False
        try:
            app_info = Play(app_id=app_id.strip())
            play_info = app_info.get_details()
            time.sleep(0.5)
            if derived:
                if "reviewsSentiment" in derived: # added
                    reviews = app_info.get_reviews(sort='relevance')
                    if len(reviews) > 0:
                        play_info['reviewsSentiment'] = process_reviews_sentiment(reviews)
                    else:
                        play_info['reviewsSentiment'] = np.nan

                if "ratingsStd" in derived or "ratingsSkew" in derived: # added
                    # process histogram
                    reviews_dist = np.concatenate([np.full(n, i+1) for i, n in enumerate(play_info['histogram'])])

                    if len(reviews_dist) > 0:
                        play_info['ratingsStd'] = round(np.std(reviews_dist), 4)
                        play_info['ratingsSkew'] = round(skew(reviews_dist, nan_policy='omit'), 4)
                    else:
                        play_info['ratingsStd'] = np.nan
                        play_info['ratingsSkew'] = np.nan

                if "descriptionGrammar" in derived:
                    matches = tool.check(play_info["description"])
                    play_info['descriptionGrammar'] = round((len(play_info["description"]) - len(matches))/len(play_info["description"]) * 100, 2)
                if "descriptionReadability" in derived:
                    play_info['descriptionReadability'] = textstat.flesch_kincaid_grade(play_info['description'])
                if "descriptionSentiment" in derived:
                    sia = SentimentIntensityAnalyzer()
                    play_info['descriptionSentiment'] = sia.polarity_scores(process_text(play_info['description']))['compound']
                if "developerCountry" in derived:
                    play_info['developerCountry'] = process_address(play_info['developerAddress'])
                if "developerNApps" in derived or "developerAppAgeMedian" in derived:
                    play_info['developerNApps'], play_info['developerAppAgeMedian'] = process_developer(play_info['developerId'])
                if play_info['released']:
                    play_info['releasedYear'] = int(play_info['released'][-4:])
                    play_info['releasedYears'] = datetime.now().year - play_info['releasedYear']

            if predict:
                try:
                    pred_e = generate_predictions(play_info, 'educational')
                    pred_v = generate_predictions(play_info, 'violent')
                    play_info['educational_proba'] = pred_e
                    play_info['violent_proba'] = pred_v
                except:
                    play_info["educational_proba"] = np.nan
                    play_info["violent_proba"] = np.nan

            app_found = True
        except Exception as e:
            print(e)
            not_found.append(app_id)

        if app_found:
            check = False
            count = 0

            while check == False and count < 30:
                try:
                    app = GoogleApp(app_id)
                    play_info2 = app.get_app()

                    if play_info2:
                        play_info.update(play_info2)
                        full_play_ls.append(play_info)
                        check = True
                except Exception as e:
                    print(e)

                count += 1
                time.sleep(1)

            if count == 30:
                full_play_ls.append(play_info)

        time.sleep(0.5)

    for app_id in not_found:
        app_found = False
        try:
            app_info = Play(app_id=app_id.strip())
            play_info = app_info.get_details()
            time.sleep(0.5)

            if derived:
                if "reviewsSentiment" in derived: # added
                    reviews = app_info.get_reviews(sort='relevance')
                    if len(reviews) > 0:
                        play_info['reviewsSentiment'] = process_reviews_sentiment(reviews)
                    else:
                        play_info['reviewsSentiment'] = np.nan

                if "ratingsStd" in derived or "ratingsSkew" in derived: # added
                    # process histogram
                    reviews_dist = np.concatenate([np.full(n, i+1) for i, n in enumerate(play_info['histogram'])])

                    if len(reviews_dist) > 0:
                        play_info['ratingsStd'] = round(np.std(reviews_dist), 4)
                        play_info['ratingsSkew'] = round(skew(reviews_dist, nan_policy='omit'), 4)
                    else:
                        play_info['ratingsStd'] = np.nan
                        play_info['ratingsSkew'] = np.nan

                if "descriptionGrammar" in derived:
                    matches = tool.check(play_info["description"])
                    play_info['descriptionGrammar'] = round((len(play_info["description"]) - len(matches))/len(play_info["description"]) * 100, 2)
                if "descriptionReadability" in derived:
                    play_info['descriptionReadability'] = textstat.flesch_kincaid_grade(play_info['description'])
                if "descriptionSentiment" in derived:
                    sia = SentimentIntensityAnalyzer()
                    play_info['descriptionSentiment'] = sia.polarity_scores(process_text(play_info['description']))['compound']
                if "developerCountry" in derived:
                    play_info['developerCountry'] = process_address(play_info['developerAddress'])
                if "developerNApps" in derived or "developerAppAgeMedian" in derived:
                    play_info['developerNApps'], play_info['developerAppAgeMedian'] = process_developer(play_info['developerId'])
                if play_info['released']:
                    play_info['releasedYear'] = int(play_info['released'][-4:])
                    play_info['releasedYears'] = datetime.now().year - play_info['releasedYear']

            if predict:
                try:
                    pred_e = generate_predictions(play_info, 'educational')
                    pred_v = generate_predictions(play_info, 'violent')
                    play_info['educational_proba'] = pred_e
                    play_info['violent_proba'] = pred_v
                except:
                    play_info["educational_proba"] = np.nan
                    play_info["violent_proba"] = np.nan

            app_found = True
        except Exception as e:
            print(e)
            not_found2.append(app_id)

        if app_found:
            check = False
            count = 0

            while check == False and count < 30:
                try:
                    app = GoogleApp(app_id)
                    play_info2 = app.get_app()

                    if play_info2:
                        play_info.update(play_info2)
                        full_play_ls.append(play_info)
                        check = True
                except Exception as e:
                    print(e)

                count += 1
                time.sleep(1)

            if count == 30:
                full_play_ls.append(play_info)

        time.sleep(0.5)

    if derived:
        if "descriptionGrammar" in derived:
            tool.close()


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
    # df.drop(columns=['icon', 'headerImage', 'screenshots', 'video', 'videoImage', 'descriptionHTML'], inplace=True)

    today = datetime.now()
    formatted_date = today.strftime("%m/%d/%Y")
    df["date_scraped"] = formatted_date

    first_column = df.pop('date_scraped')
    df.insert(0, 'date_scraped', first_column)


    df2 = pd.DataFrame({"appId": not_found2})

    # Using BytesIO to write to Excel format in memory
    with io.BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='apps_found', index=False)
            df2.to_excel(writer, sheet_name='not_found', index=False)

            # Access the xlsxwriter workbook and worksheet objects
            workbook  = writer.book
            worksheet1 = writer.sheets['apps_found']
            worksheet2 = writer.sheets['not_found']

            # Define a format for wrapped text.
            wrap_format = workbook.add_format({'text_wrap': True})

            # Define a format to specify row height (e.g., 20)
            row_format = workbook.add_format()
            row_format.set_text_wrap(True)  # If you also want to wrap text
            row_height = 100  # Adjust the height as necessary

            # Set text wrap format and row height for non-header rows in both sheets
            for row_num in range(1, len(df) + 1):  # Start from 1 to skip the header
                worksheet1.set_row(row_num, row_height, wrap_format)



        # Important: You must seek back to the beginning of the buffer after writing
        buffer.seek(0)
        return dcc.send_bytes(buffer.getvalue(), "play_features.xlsx")









########################################################################
# APPLE SCRAPER FUNCTIONS
@dash.callback(
    Output('dl-apple', 'data'),
    [
        Input('confirm-button-apple', 'n_clicks'),
    ],
    [
        #State('predict-checkbox', 'checked'),
        State('dl-input-apple', 'value'),
        # State('filters-derived-apple', 'value') # added
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
def update_apple_info(set_progress, click, apps): # , derived):
    """
    Function to scrape data on Apple iTunes store items such as apps and download them in an .xlsx file.

    Parameters
    ----------
    apps (str) - string of app/song/etc. IDs

    Returns
    -------
    df (download) - dataframe of the scraped ID information
    """

    full_apple_ls = []
    not_found = []
    not_found2 = []
    apps_ls = apps.split('\n')
    n_apps = len(apps_ls)

    for idx, app_id in enumerate(apps_ls):
        print(f"Fetching {idx + 1}/{n_apps}: {app_id}")
        set_progress((idx + 1, f"{int((idx + 1) / n_apps * 100)} %", n_apps))
        app_found = False
        try:
            app_info = Apple(app_id=app_id.strip())
            apple_details = app_info.get_details()
            time.sleep(0.5)

            # print(apple_details)

            # if derived:
            #     if "reviewsSentiment" in derived: # added
            #             reviews = app_info.get_reviews(sort='relevance')
            #             if len(reviews) > 0:
            #                 apple_details['reviewsSentiment'] = process_reviews_sentiment(reviews)
            #             else:
            #                 apple_details['reviewsSentiment'] = np.nan

            app_found = True
        except Exception as e:
            print(e)
            not_found.append(app_id)

        if app_found:
            check = False
            count = 0

            while check == False and count < 30:
                try:
                    app = AppleApp(id=f"{app_id}")
                    apple_details2 = app.get_app()

                    if apple_details2:
                        apple_details.update(apple_details2)
                        full_apple_ls.append(apple_details)
                        check = True
                except Exception as e:
                    print(e)

                count += 1
                time.sleep(1)

            if count == 30:
                full_apple_ls.append(apple_details)


        time.sleep(0.5)

    for app_id in not_found:
        app_found = False

        try:
            app_info = Apple(app_id=app_id.strip())
            apple_details = app_info.get_details()
            time.sleep(0.5)

            # print(apple_details)

            # if derived:
            #     if "reviewsSentiment" in derived: # added
            #             reviews = app_info.get_reviews(sort='relevance')
            #             if len(reviews) > 0:
            #                 apple_details['reviewsSentiment'] = process_reviews_sentiment(reviews)
            #             else:
            #                 apple_details['reviewsSentiment'] = np.nan

            app_found = True
        except Exception as e:
            print(e)
            not_found2.append(app_id)

        if app_found:
            check = False
            count = 0

            while check == False and count < 30:
                try:
                    app = AppleApp(id=f"{app_id}")
                    apple_details2 = app.get_app()

                    if apple_details2:
                        apple_details.update(apple_details2)
                        full_apple_ls.append(apple_details)
                        check = True
                except Exception as e:
                    print(e)

                count += 1
                time.sleep(1)

            if count == 30:
                full_apple_ls.append(apple_details)


        time.sleep(0.5)

    df = pd.DataFrame(full_apple_ls)
    # print(df)
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
    # df.drop(columns=['ipadScreenshotUrls', 'appletvScreenshotUrls', 'artworkUrl60', 'artworkUrl512', 'artworkUrl100', 'screenshotUrls'], inplace=True)

    today = datetime.now()
    formatted_date = today.strftime("%m/%d/%Y")
    df["date_scraped"] = formatted_date

    first_column = df.pop('date_scraped')
    df.insert(0, 'date_scraped', first_column)

    df2 = pd.DataFrame({"appId": not_found2})

    # Using BytesIO to write to Excel format in memory
    with io.BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='apps_found', index=False)
            df2.to_excel(writer, sheet_name='not_found', index=False)

            # Access the xlsxwriter workbook and worksheet objects
            workbook  = writer.book
            worksheet1 = writer.sheets['apps_found']
            worksheet2 = writer.sheets['not_found']

            # Define a format for wrapped text.
            wrap_format = workbook.add_format({'text_wrap': True})

            # Define a format to specify row height (e.g., 20)
            row_format = workbook.add_format()
            row_format.set_text_wrap(True)  # If you also want to wrap text
            row_height = 100  # Adjust the height as necessary

            # Set text wrap format and row height for non-header rows in both sheets
            for row_num in range(1, len(df) + 1):  # Start from 1 to skip the header
                worksheet1.set_row(row_num, row_height, wrap_format)



        # Important: You must seek back to the beginning of the buffer after writing
        buffer.seek(0)
        return dcc.send_bytes(buffer.getvalue(), "apple_features.xlsx")









########################################################################
# YOUTUBE SCRAPER FUNCTIONS
async def get_videos(click, apps):
    """
    Function to get video details based on the list provided.

    Parameters
    ----------
    apps (str) - video IDs

    Returns
    -------
    df - dataframe of thevideo details

    """
    scraper = YoutubeScraper()

    video_ids = apps.split()
    video_df = await scraper.video_metadata(video_ids)

    return video_df




@dash.callback(
    Output('dl-you', 'data'),
    [
        Input('confirm-button-you', 'n_clicks'),
    ],
    [
        State('dl-input-you', 'value'),
        State('you-filters', 'value')
    ],
    # running=[
        # (Output("dl-you-progress", "animated"), True, False),
    # ],
    # progress=[
    #     Output("dl-you-progress", "value"),
    #     Output("dl-you-progress", "label"),
    #     Output("dl-you-progress", "max")
    # ],
    prevent_initial_call=True,
    background=True
)
def update_youtube_info(click, apps, filters):
    """
    Function to scrape data on YouTube videos and download them in an .xlsx file.

    Parameters
    ----------
    apps (str) - string of video IDs

    Returns
    -------
    df (download) - dataframe of the scraped video ID information
    """

    df = asyncio.run(get_videos(click, apps))

    #  not_found = [item for item in apps.split("\n") if item not in df["video_id"].to_list()]

    if not filters:
        today = datetime.now()
        formatted_date = today.strftime("%m/%d/%Y")
        df["date_scraped"] = formatted_date

        first_column = df.pop('date_scraped')
        df.insert(0, 'date_scraped', first_column)
        return dcc.send_data_frame(df.to_excel, "youtube_features.xlsx", index=False)
    else:
        df.drop(columns=df.columns.difference(filters), inplace=True)

        today = datetime.now()
        formatted_date = today.strftime("%m/%d/%Y")
        df["date_scraped"] = formatted_date

        first_column = df.pop('date_scraped')
        df.insert(0, 'date_scraped', first_column)
        return dcc.send_data_frame(df.to_excel, "youtube_features.xlsx", index=False)
