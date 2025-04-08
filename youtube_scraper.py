from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup

import aiohttp
import asyncio
import json
import pandas as pd
import re

class YoutubeScraper:
    YOUTUBE_VIDEO_PREFIX = 'https://www.youtube.com/watch?v='
    # YOUTUBE_SEARCH_PREFIX = 'https://www.youtube.com/results?search_query='

    def __init__(self, proxy_url=None, delay=1):
        self.proxy_url = proxy_url
        self.delay = delay
        self.session = self.open_session()

    def open_session(self):
        """
        Function to create an aiohttp session with or without a proxy.

        Parameters
        ----------
        None

        Returns
        -------
        aiohttp session
        """
        if self.proxy_url:
            return aiohttp.ClientSession(connector=ProxyConnector.from_url(self.proxy_url))
        return aiohttp.ClientSession()

    async def close_session(self):
        """
        Function to close the session when done.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        await self.session.close()

    def get_video(self, video_id, response):
        """
        Function to collect all data scraped for an video and return it as a dictionary.

        Parameters
        ----------
        video_id - str of the YouTube video_id
        response - page response for specific video_id

        Returns
        -------
        row - dict of key value pairs of the data
        """
        initial_player_response = self.get_var_page_data(response, 'ytInitialPlayerResponse')
        initial_data = self.get_var_page_data(response, 'ytInitialData')

        row = {}
        row['video_id'] = video_id

        if self.get_is_unavailable(initial_player_response, initial_data):
            row['unavailable'] = True
            return row

        if self.get_is_removed(initial_player_response):
            row['unavailable'] = True
            row['removed'] = True
            return row

        row['private'] = False
        row['requires_payment'] = False
        row['is_livestream_recording_not_available'] = False

        # check if video is playable
        if initial_player_response['playabilityStatus']['status'] in ['OK', 'LOGIN_REQUIRED']:
            # check if video is private
            if self.get_is_private(initial_player_response):
                row['private'] = True
                return row

            row['requires_payment'] = self.get_requires_payment(initial_player_response)
            row['livestream_recording_not_available'] = self.get_livestream_recording_unavailable(initial_player_response)

        row['title'] = initial_player_response['videoDetails']['title']
        row['description'] = initial_player_response['videoDetails']['shortDescription']
        row['view_count'] = int(initial_player_response['videoDetails']['viewCount'])
        #row['like_count']= self.get_like_count(initial_data)
        row['length_seconds'] = int(initial_player_response['videoDetails']['lengthSeconds'])
        row['channel_name'] = initial_player_response['videoDetails']['author']
        row['channel_id'] = initial_player_response['videoDetails']['channelId']
        row['channel_url'] = initial_player_response['microformat']['playerMicroformatRenderer']['ownerProfileUrl']
        row['family_safe'] = initial_player_response['microformat']['playerMicroformatRenderer']['isFamilySafe']
        row['unlisted'] = initial_player_response['microformat']['playerMicroformatRenderer']['isUnlisted']
        row['live_content'] = initial_player_response['videoDetails']['isLiveContent']
        row['removed'] = False
        row['unavailable'] = False
        row['category'] = initial_player_response['microformat']['playerMicroformatRenderer']['category']
        row['upload_date'] = initial_player_response['microformat']['playerMicroformatRenderer']['uploadDate']
        row['publish_date'] = initial_player_response['microformat']['playerMicroformatRenderer']['publishDate']
        row['video_recommendations'] = self.get_recommendations(initial_data)

        return row

    def get_var_page_data(self, response, var_name):
        """
        Function to get page data for specific var.

        Parameters
        ----------
        response - page response for specific video_id
        var_name - str of the var sought

        Returns
        -------
        Either a dictionary for the var or None
        """
        soup = BeautifulSoup(response, 'html.parser')
        scripts = soup.find('body').find_all('script')
        pattern = re.compile(r'= (.*});')

        for script in scripts:
            if str(script) != None and 'var ' + var_name in str(script):
                    return json.loads(pattern.findall((str(script)))[0])

        return None

    async def get_video_page(self, video_id):
        """
        Function to fetch the video page for a given video ID.

        Parameters
        ----------
        video_id - str of the video_id

        Returns
        -------
        video_id
        text from the GET request
        """
        async with self.session.get(self.YOUTUBE_VIDEO_PREFIX + video_id) as response:
            response.raise_for_status()
            await asyncio.sleep(self.delay)
            return video_id, await response.text()

    def get_is_private(self, initial_player_response):
        """
        Function to determine whether or not a video is private.

        Parameters
        ----------
        initial_player_response - response data on the specific video

        Returns
        -------
        TRUE/FALSE value
        """
        print(initial_player_response)
        print()
        return initial_player_response['playabilityStatus']['status'] == 'LOGIN_REQUIRED'

    def get_is_removed(self, initial_player_response):
        """
        Function to determine whether or not a video has been removed.

        Parameters
        ----------
        initial_player_response - response data on the specific video

        Returns
        -------
        TRUE/FALSE value
        """
        try:
            return initial_player_response['playabilityStatus']['reason'] in ['This video has been removed for violating YouTube\'s Community Guidelines.', "This video has been removed for violating YouTube\'s Community Guidelines", "This video has been removed for violating YouTube\'s Terms of Service"]
        except KeyError as e:
            if e.args[0] == 'reason':
                return False

    def get_is_unavailable(self, initial_player_response, initial_data):
        """
        Function to determine whether or not a video is unavailable.

        Parameters
        ----------
        initial_player_response - response data on the specific video

        Returns
        -------
        TRUE/FALSE value
        """
        try:
            return 'contents' not in initial_data or initial_player_response['playabilityStatus']['reason'] == 'Video unavailable'
        except KeyError as e:
            if e.args[0] == 'reason':
                return False

    def get_like_count(self, initial_data):
        """
        Function to get video like counts for a specific video_id.

        Parameters
        ----------
        initial_data - page data on the specific video

        Returns
        -------
        likes - int of number of likes
        """
        # Like count index is variable; we find it here before trying to access
        like_count_index = 0

        for item in initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents']:
            if 'videoPrimaryInfoRenderer' in item:
                break
            like_count_index += 1

        # Get like count
        like_text = initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][like_count_index]['videoPrimaryInfoRenderer']['videoActions']['menuRenderer']['topLevelButtons'][0]['toggleButtonRenderer']['accessibilityData']['accessibilityData']['label']

        if like_text == 'I like this':
            return None

        likes = int(like_text.split('with ')[1].split(' ')[0].replace(',', ''))
        return likes

    def get_livestream_recording_unavailable(self, initial_player_response):
        """
        Function to determine whether or not livestream recording is available.

        Parameters
        ----------
        initial_player_response - response data on the specific livestream

        Returns
        -------
        TRUE/FALSE value
        """
        try:
            return initial_player_response['playabilityStatus']['reason'] == 'This live stream recording is not available.'
        except KeyError as e:
            if e.args[0] == 'reason':
                return False

    def get_recommendations(self, initial_data):
        """
        Function to get video recommendations for a specific video_id.

        Parameters
        ----------
        initial_data - page data on the specific video

        Returns
        -------
        recommendations - list of video_ids
        """
        recommendations_list = initial_data['contents']['twoColumnWatchNextResults']['secondaryResults']['secondaryResults']['results']

        recommendations = []
        for recommendation in recommendations_list:
            if 'compactVideoRenderer' in recommendation:
                recommendations.append(recommendation['compactVideoRenderer']['videoId'])

        return recommendations

    def get_requires_payment(self, initial_player_response):
        """
        Function to determine whether or not a video requires payment to watch.

        Parameters
        ----------
        initial_player_response - response data on the specific video

        Returns
        -------
        TRUE/FALSE value
        """
        try:
            return initial_player_response['playabilityStatus']['reason'] == 'This video requires payment to watch.'
        except KeyError as e:
            if e.args[0] == 'reason':
                return False

    # async def get_search(self, search_term):
    #     async with self.session.get(self.YOUTUBE_SEARCH_PREFIX + search_term) as response:
    #         return (search_term, await response.text())

    # async def search_results(self, search_term):
    #     # Get search response
    #     response = (await (self.get_search(self.session, search_term)))[1]
    #     await session.close()

    #     initial_data = self.get_var_page_data(response, 'ytInitialData')

    #     # Recommendations count index is variable; we find it here before trying to access
    #     recommendations_index = 0
    #     recommendations_key = initial_data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']

    #     for item in recommendations_key:
    #         if 'videoRenderer' in item['itemSectionRenderer']['contents'][0] or \
    #             len(item['itemSectionRenderer']['contents']) > 15: # Promotional slots have relatively few items in each section
    #             break
    #         recommendations_index += 1

    #     recommendations = []

    #     for recommendation in recommendations_key[recommendations_index]['itemSectionRenderer']['contents']:
    #         try:
    #             recommendations.append(recommendation['videoRenderer']['videoId'])
    #         except KeyError as e:
    #             if e.args[0] == 'videoRenderer':
    #                 pass

    #     return recommendations

    # async def get_video_metadata(self, video_ids):
    #     """
    #     Function to fetch metadata for a list of video IDs.

    #     Parameters
    #     ----------
    #     video_ids - list of video_ids

    #     Returns
    #     -------
    #     pandas DataFrame of all video_ids scraped
    #     """
    #     tasks = [self.get_video_page(video_id) for video_id in video_ids]
    #     responses = dict(await asyncio.gather(*tasks))

    #     rows = [self.get_video(video_id, response) for video_id, response in responses.items()]
    #     return pd.DataFrame(rows).replace(r'^\s*$', None, regex=True)