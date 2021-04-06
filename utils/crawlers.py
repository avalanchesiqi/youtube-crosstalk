import sys, time, re, json, requests, random
from urllib.parse import parse_qs, quote, unquote, urlparse
from bs4 import BeautifulSoup
from googleapiclient import discovery
from selenium import webdriver

USER_AGENT_LIST = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36']

# AllSides source url
ALLSIDES_SOURCE_URL = 'https://www.allsides.com{source_href}'

# MBFC source url
MBFC_SOURCE_URL = 'https://mediabiasfactcheck.com/{page}/'

# YouTube webpage url, API service and version
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
YOUTUBE_CHANNEL_ABOUT = 'https://www.youtube.com/channel/{channel_id}/about'
YOUTUBE_CHANNEL_SUBSCRIPTION = 'https://www.youtube.com/channel/{channel_id}/channels?view=56&flow=grid'
YOUTUBE_CHANNEL_FEATURED = 'https://www.youtube.com/channel/{channel_id}/channels?view=60&flow=grid'
YOUTUBE_USER_ABOUT = 'https://www.youtube.com/user/{user_name}/about'
YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v={video_id}'
YOUTUBE_PLAYLIST_URL = 'https://www.youtube.com/playlist?list={playlist_id}'
YOUTUBE_BROWSER_AJAX_URL = 'https://www.youtube.com/browse_ajax'
YOUTUBE_COMMENTS_AJAX_URL_OLD = 'https://www.youtube.com/comment_ajax'
YOUTUBE_COMMENTS_AJAX_URL_NEW = 'https://www.youtube.com/comment_service_ajax'

START_DATE = '2020-01-01'


def format_url(url):
    parsed_url = urlparse(url.lower())
    return '{0}://{1}'.format(parsed_url.scheme, parsed_url.netloc.split(':')[0])


def get_domain(url):
    return re.sub(r'www\d?.', '', urlparse(url.lower()).netloc.split(':')[0])


def get_search_request(title):
    return 'https://youtube.com/results?search_query={0}&sp=EgIQAg%253D%253D'.format(quote(title))


def find_value(html, key, num_chars=2, separator='"'):
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find(separator, pos_begin)
    return html[pos_begin: pos_end]


def search_dict(partial, key):
    if isinstance(partial, dict):
        for k, v in partial.items():
            if k == key:
                yield v
            else:
                for o in search_dict(v, key):
                    yield o
    elif isinstance(partial, list):
        for i in partial:
            for o in search_dict(i, key):
                yield o


def ajax_request(session, url, params=None, data=None, headers=None, max_retry=5, sleep=20):
    for idx_request in range(max_retry):
        response = session.post(url, params=params, data=data, headers=headers)
        time.sleep(1)
        if response.status_code == 200:
            ret_json = response.json()
            if isinstance(ret_json, list):
                ret_json = [x for x in ret_json if 'response' in x][0]
            ret_json.update({'num_request': idx_request + 1})
            return ret_json
        elif response.status_code in [403, 413]:
            return {'error': 'Comments are turned off', 'num_request': idx_request + 1}
        time.sleep(sleep)
    return {'error': 'Unknown error {0}'.format(response.status_code), 'num_request': max_retry}


# def find_channel_description(soup):
#     description = soup.find('div', {'class': 'about-description'}).text.lower()
#     if description is not None:
#         return description
#     return ''


def match_website_on_twitter_page(user_json, website_url):
    domain = get_domain(website_url)
    if 'entities' in user_json:
        if 'url' in user_json['entities']:
            if 'urls' in user_json['entities']['url']:
                if len(user_json['entities']['url']['urls']) > 0:
                    if 'expanded_url' in user_json['entities']['url']['urls'][0]:
                        if user_json['entities']['url']['urls'][0]['expanded_url'] is not None:
                            expand_url = user_json['entities']['url']['urls'][0]['expanded_url'].lower()
                            if expand_url is not None:
                                if domain == get_domain(expand_url):
                                    # the paths should be both empty or the same
                                    if urlparse(website_url).path == '' or urlparse(website_url).path == '/':
                                        if urlparse(expand_url).path == '' or urlparse(expand_url).path == '/':
                                            return True
                                    elif urlparse(website_url).path.strip('/') == urlparse(expand_url).path.strip('/'):
                                        return True

                            redirected_expand_url = None
                            try:
                                redirected_expand_url = requests.get(expand_url,
                                                                     headers={'User-Agent': random.choice(USER_AGENT_LIST)},
                                                                     allow_redirects=True).url
                            except:
                                pass
                            if redirected_expand_url is not None:
                                if domain == get_domain(redirected_expand_url):
                                    # the paths should be both empty or the same
                                    if urlparse(website_url).path == '' or urlparse(website_url).path == '/':
                                        if urlparse(redirected_expand_url).path == '' or urlparse(redirected_expand_url).path == '/':
                                            return True
                                    elif urlparse(website_url).path.strip('/') == urlparse(redirected_expand_url).path.strip('/'):
                                        return True
    return False


def match_links_on_youtube_page(response, website_url, tw_handle):
    domain = get_domain(website_url)
    if response:
        html = response.text
        try:
            initial_data = json.loads(find_value(html, 'window["ytInitialData"] = ', 0, '\n').rstrip(';'))
            # print(json.dumps(initial_data))
        except:
            return False

        links = next(search_dict(initial_data, 'primaryLinks'), [])
        for link in links:
            url = link['navigationEndpoint']['urlEndpoint']['url']
            redirected_url = parse_qs(unquote(urlparse(url).query))
            if 'q' in redirected_url:
                redirected_url = redirected_url['q'][0]
                if redirected_url.startswith('http'):
                    redirected_domain = get_domain(redirected_url)
                else:
                    redirected_domain = re.sub(r'(https?://)?(www.)?', '', redirected_url).split('/', 1)[0]
                redirected_url = re.sub(r'(https?://)?(www.)?', '', redirected_url)
                redirected_url = redirected_url.strip('/')
                # print('>>>', redirected_url)
                if redirected_url.startswith('twitter.com/'):
                    if tw_handle == redirected_url.split('twitter.com/')[1].split('?')[0]:
                        return True
                elif domain == redirected_domain:
                    return True

        description = next(search_dict(initial_data, 'description'), {})
        if len(description) > 0:
            description = description['simpleText'].replace('\n', ' ')
            print('>>> channel description:', description)
            if domain in description:
                return True
    return False


def _extract_text(block):
    if 'simpleText' in block:
        return block['simpleText']
    elif 'runs' in block:
        return block['runs'][0]['text']
    return 'NA'


def get_video_upload(video_id):
    session = requests.Session()
    session.headers['User-Agent'] = random.choice(USER_AGENT_LIST)

    response = session.get(YOUTUBE_VIDEO_URL.format(video_id=video_id))
    # too many requests, IP is banned by YouTube
    if response.status_code == 429:
        return None
    if response is not None:
        html = response.text

        try:
            initial_player_response = json.loads(find_value(html, 'window["ytInitialPlayerResponse"] = ', 0, '\n').rstrip(';'))
            # print(json.dumps(initial_player_response))
        except:
            return None

        if 'videoDetails' not in initial_player_response \
                or 'microformat' not in initial_player_response \
                or 'playerMicroformatRenderer' not in initial_player_response['microformat']:
            print('xxx private or unavailable video {0}'.format(video_id))
            return None

        microformat_renderer = initial_player_response['microformat']['playerMicroformatRenderer']
        publish_date = microformat_renderer['publishDate']
        return publish_date


def get_videos_from_playlist(playlist_id):
    """Get the video list given a playlist, max 20000 videos, in reverse chronological order."""
    session = requests.Session()
    session.headers['User-Agent'] = random.choice(USER_AGENT_LIST)

    playlist_videos = []
    response = session.get(YOUTUBE_PLAYLIST_URL.format(playlist_id=playlist_id))
    time.sleep(1)
    if response is not None:
        html = response.text
        session_token = find_value(html, 'XSRF_TOKEN', 3)

        initial_data = json.loads(find_value(html, 'window["ytInitialData"] = ', 0, '\n').rstrip(';'))

        for video in search_dict(initial_data, 'playlistVideoRenderer'):
            playlist_videos.append(video['videoId'])

        if len(playlist_videos) > 0:
            earliest_publish_date = get_video_upload(playlist_videos[-1])
            print(earliest_publish_date)
            if earliest_publish_date is not None and earliest_publish_date < START_DATE:
                return playlist_videos

        ncd = next(search_dict(initial_data, 'continuationEndpoint'), None)
        if ncd:
            continuations = [(ncd['continuationCommand']['token'], ncd['clickTrackingParams'])]

            while continuations:
                continuation, itct = continuations.pop()
                response_json = ajax_request(session,
                                             YOUTUBE_BROWSER_AJAX_URL,
                                             params={'referer': YOUTUBE_PLAYLIST_URL.format(playlist_id=playlist_id),
                                                     'pbj': 1,
                                                     'ctoken': continuation,
                                                     'continuation': continuation,
                                                     'itct': itct},
                                             data={'session_token': session_token},
                                             headers={'X-YouTube-Client-Name': '1',
                                                      'X-YouTube-Client-Version': '2.20200207.03.01'})

                if len(response_json) == 0:
                    break
                if next(search_dict(response_json, 'externalErrorMessage'), None):
                    raise Exception('Error returned from server: ' + next(search_dict(response_json, 'externalErrorMessage')))
                elif 'error' in response_json:
                    raise Exception(response_json['error'])

                # Ordering matters. The newest continuations should go first.
                continuations = [(ncd['continuationCommand']['token'], ncd['clickTrackingParams']) for ncd in search_dict(response_json, 'continuationEndpoint')] + continuations

                for video in search_dict(response_json, 'playlistVideoRenderer'):
                    playlist_videos.append(video['videoId'])

                earliest_publish_date = get_video_upload(playlist_videos[-1])
                print(earliest_publish_date)
                if earliest_publish_date is not None and earliest_publish_date < START_DATE:
                    return playlist_videos

    return playlist_videos


def get_subscriptions_from_channel(channel_id, target='subscription'):
    """Get description and subscriptions/featured channels given a channel."""
    session = requests.Session()
    session.headers['User-Agent'] = random.choice(USER_AGENT_LIST)

    if target == 'subscription':
        request_url = YOUTUBE_CHANNEL_SUBSCRIPTION
    else:
        request_url = YOUTUBE_CHANNEL_FEATURED

    channel_title = ''
    channel_description = ''
    subscriptions = []
    response = session.get(request_url.format(channel_id=channel_id))
    time.sleep(1)
    if response is not None:
        html = response.text
        session_token = find_value(html, 'XSRF_TOKEN', 3)

        initial_data = json.loads(find_value(html, 'window["ytInitialData"] = ', 0, '\n').rstrip(';'))
        # print(json.dumps(initial_data))

        channel_json = next(search_dict(initial_data, 'channelMetadataRenderer'), None)
        if channel_json:
            channel_title = channel_json['title']
            channel_description = channel_json['description']

        content_types = next(search_dict(initial_data, 'contentTypeSubMenuItems'), [])

        has_target = False
        if target == 'subscription':
            for content_type in content_types:
                title = content_type['title'].lower()
                if title == 'subscriptions':
                    has_target = True
                    break
        else:
            for content_type in content_types:
                title = content_type['title'].lower()
                if title != 'subscriptions':
                    has_target = True
                    break

        if has_target:
            visited_channels = set()
            for grid_channel_renderer in search_dict(initial_data, 'gridChannelRenderer'):
                subscribed_channel_id = grid_channel_renderer['channelId']
                if subscribed_channel_id not in visited_channels:
                    subscribed_title = grid_channel_renderer['title']['simpleText']
                    if 'videoCountText' in grid_channel_renderer:
                        video_count = _extract_text(grid_channel_renderer['videoCountText']).split()[0]
                    else:
                        video_count = '0'
                    if 'subscriberCountText' in grid_channel_renderer:
                        subscriber_count = _extract_text(grid_channel_renderer['subscriberCountText']).split()[0]
                    else:
                        subscriber_count = '0'

                    subscriptions.append((subscribed_channel_id, subscribed_title, video_count, subscriber_count))
                    visited_channels.add(subscribed_channel_id)

            ncd = next(search_dict(initial_data, 'nextContinuationData'), None)
            if ncd:
                continuations = [(ncd['continuation'], ncd['clickTrackingParams'])]

                while continuations:
                    continuation, itct = continuations.pop()
                    response_json = ajax_request(session,
                                                 YOUTUBE_BROWSER_AJAX_URL,
                                                 params={'referer': request_url.format(channel_id=channel_id),
                                                         'dpr': 1,
                                                         'ctoken': continuation,
                                                         'continuation': continuation,
                                                         'itct': itct},
                                                 data={'session_token': session_token},
                                                 headers={'X-YouTube-Client-Name': '1',
                                                          'X-YouTube-Client-Version': '2.20200903.02.02'})

                    if len(response_json) == 0:
                        break
                    if next(search_dict(response_json, 'externalErrorMessage'), None):
                        raise Exception('Error returned from server: ' + next(search_dict(response_json, 'externalErrorMessage')))
                    elif 'error' in response_json:
                        raise Exception(response_json['error'])

                    # Ordering matters. The newest continuations should go first.
                    continuations = [(ncd['continuation'], ncd['clickTrackingParams']) for ncd in search_dict(response_json, 'nextContinuationData')] + continuations

                    for grid_channel_renderer in search_dict(response_json, 'gridChannelRenderer'):
                        subscribed_channel_id = grid_channel_renderer['channelId']
                        subscribed_title = grid_channel_renderer['title']['simpleText']
                        if 'videoCountText' in grid_channel_renderer:
                            video_count = _extract_text(grid_channel_renderer['videoCountText']).split()[0]
                        else:
                            video_count = '0'
                        if 'subscriberCountText' in grid_channel_renderer:
                            subscriber_count = _extract_text(grid_channel_renderer['subscriberCountText']).split()[0]
                        else:
                            subscriber_count = '0'
                        subscriptions.append((subscribed_channel_id, subscribed_title, video_count, subscriber_count))
                        visited_channels.add(subscribed_channel_id)

    if target == 'subscription':
        return {'channel_id': channel_id, 'title': channel_title, 'description': channel_description, 'subscriptions': subscriptions}
    else:
        return {'channel_id': channel_id, 'title': channel_title, 'description': channel_description, 'featured_channels': subscriptions}


def get_webdriver(headless=False, adblock=False):
    chrome_options = webdriver.ChromeOptions()
    # Option 1: mute the browser
    chrome_options.add_argument('--mute-audio')
    # Option 2: headless browser
    if headless:
        chrome_options.add_argument('--headless')
    # Option 3: do not load images
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    # Option 4: add YouTube Adblock
    if adblock:
        path_to_extension = '../conf/webdriver/Adblock-Youtube.crx'
        chrome_options.add_extension(path_to_extension)

    if sys.platform == 'win32':
        driver_path = '../conf/webdriver/chromedriver.exe'
    elif sys.platform == 'darwin':
        driver_path = '../conf/webdriver/chromedriver_mac64'
    else:
        driver_path = '../conf/webdriver/chromedriver_linux64'
    driver = webdriver.Chrome(driver_path, options=chrome_options)
    return driver


def get_webpage_items_selenium(driver, channel_page, reversed=False):
    """Simulate a browser behavior to scroll via selenium."""
    driver.get(channel_page)

    # Scroll down to bottom to get all item ids
    # Get current height
    last_height = driver.execute_script('return document.documentElement.scrollHeight')
    num_scroll = 1
    while True:
        # Scroll down to the bottom of current page
        driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight);')
        # Wait to load page, check every 4 seconds for 15 rounds (60 seconds in total)
        num_round = 0
        new_height = last_height
        while num_round < 15:
            time.sleep(4)
            # Calculate new scroll height
            new_height = driver.execute_script('return document.documentElement.scrollHeight')
            num_round += 1
            print('scroll-round: {0:>3}-{1}'.format(num_scroll, num_round))
            if new_height > last_height:
                break
        num_scroll += 1
        # Compare with last scroll height
        if new_height == last_height:
            print('in total, scroll {0} time'.format(num_scroll))
            break
        last_height = new_height

    time.sleep(10)

    item_list = []
    visited_items = set()
    soup = BeautifulSoup(driver.page_source, 'lxml')
    item_blocks = soup.find_all('a', href=True, id='video-title')
    for item_block in item_blocks:
        item_list.append((item_block['href'], item_block.text))
        visited_items.add(item_block['href'])

    # if we want to check the webpage in reverse order, check the last element in every 10 scrolls
    if channel_page.endswith('videos') and reversed:
        reverse_channel_page = channel_page + '?view=0&sort=da&flow=grid'
        driver.get(reverse_channel_page)

        # Scroll down to bottom to get all item ids
        # Get current height
        last_height = driver.execute_script('return document.documentElement.scrollHeight')
        num_rev_scroll = 1
        while True:
            # Scroll down to the bottom of current page
            driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight);')
            # Wait to load page, check every 4 seconds for 15 rounds (60 seconds in total)
            num_round = 0
            new_height = last_height
            while num_round < 15:
                time.sleep(4)
                # Calculate new scroll height
                new_height = driver.execute_script('return document.documentElement.scrollHeight')
                num_round += 1
                print('reversed scroll-round: {0:>3}-{1}'.format(num_rev_scroll, num_round))
                if new_height > last_height:
                    break
            num_rev_scroll += 1
            # Compare with last scroll height
            if new_height == last_height:
                print('in reversed total, scroll {0} time'.format(num_rev_scroll))
                break
            if num_rev_scroll % 10 == 0:
                soup = BeautifulSoup(driver.page_source, 'lxml')
                reversed_item_blocks = soup.find_all('a', href=True, id='video-title')[::-1]
                if reversed_item_blocks[0]['href'] in visited_items:
                    for item_block in reversed_item_blocks:
                        if item_block['href'] not in visited_items:
                            item_list.append((item_block['href'], item_block.text))
                    break
            last_height = new_height

    return item_list


class YTCrawler(object):
    def __init__(self):
        self.key = None
        self.client = None

    def set_key(self, key):
        """ Set developer key.
        """
        self.key = key
        self.client = discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                                      developerKey=self.key, cache_discovery=False)

    def get_channel_id(self, yt_user, parts):
        """ Call the API's channels().list method to get the channel id.
        """
        # exponential back-off
        for i in range(0, 3):
            try:
                response = self.client.channels().list(forUsername=yt_user, part=parts).execute()
                if response is not None:
                    if 'items' in response and len(response['items']) > 0:
                        res_json = response['items'][0]
                        channel_id = res_json['id']
                        return channel_id
                    else:
                        return ''
            except Exception as e:
                print('xxx Error! failed to get channel id for user {0}'.format(yt_user))
                print(str(e))
                time.sleep(2 ** i)
        return ''

    def check_channel_id(self, yt_id, parts):
        """ Call the API's channels().list method to get the channel id.
        """
        # exponential back-off
        for i in range(0, 3):
            try:
                response = self.client.channels().list(id=yt_id, part=parts).execute()
                if response is not None:
                    if 'items' in response and len(response['items']) > 0:
                        res_json = response['items'][0]
                        channel_id = res_json['id']
                        return channel_id
                    else:
                        return ''
            except Exception as e:
                print('xxx Error! failed to check channel id for channel {0}'.format(yt_id))
                print(str(e))
                time.sleep(2 ** i)
        return ''

    def get_channel_snippet(self, yt_id, parts):
        """ Call the API's channels().list method to get the channel snippet and statistics.
        """
        # exponential back-off
        for i in range(0, 3):
            try:
                response = self.client.channels().list(id=yt_id, part=parts).execute()
                if response is not None:
                    if 'items' in response and len(response['items']) > 0:
                        res_json = response['items'][0]
                        yt_title = res_json['snippet']['title']
                        yt_description = res_json['snippet']['description']
                        yt_published_at = res_json['snippet']['publishedAt']
                        if 'country' in res_json['snippet']:
                            yt_country = res_json['snippet']['country']
                        else:
                            yt_country = ''
                        yt_video_count = res_json['statistics']['videoCount']
                        yt_view_count = res_json['statistics']['viewCount']
                        yt_subscriber_count = res_json['statistics']['subscriberCount']
                        return {'yt_title': yt_title, 'yt_description': yt_description, 'yt_country': yt_country,
                                'yt_published_at': yt_published_at, 'yt_video_count': yt_video_count,
                                'yt_view_count': yt_view_count, 'yt_subscriber_count': yt_subscriber_count}
                    else:
                        return {}
            except Exception as e:
                print('xxx Error! failed to get channel snippet for channel {0}'.format(yt_id))
                print(str(e))
                time.sleep(2 ** i)
        return ''

    def search_videos(self, query, published_after):
        """ Call the API's search().list method to search videos.
        maxResults is 50.
        """
        videos = []
        next_page_token = ''
        max_results = 50
        end_flag = False
        while not end_flag:
            # exponential back-off
            for i in range(0, 3):
                try:
                    response = self.client.search().list(
                        part='snippet',
                        maxResults=max_results,
                        order='date',
                        publishedAfter=published_after,
                        q=query,
                        type='video',
                        pageToken=next_page_token
                    ).execute()
                    results = response['items']
                    videos.extend(results)
                    num_result_on_page = response['pageInfo']['resultsPerPage']
                    if num_result_on_page < max_results \
                            or len(results) == 0 \
                            or 'nextPageToken' not in response:
                        end_flag = True
                    else:
                        next_page_token = response['nextPageToken']
                except Exception as e:
                    print(f'xxx Error! failed to get videos for query {query}')
                    print(str(e))
                    time.sleep(2 ** i)
        return videos

    def fetch_comments(self, video_id):
        """ Call the API's commentThreads().list method to fetch comments.
        maxResults is 100.
        """
        comments = []
        next_page_token = ''
        max_results = 100
        end_flag = False
        while not end_flag:
            # exponential back-off
            for i in range(0, 3):
                try:
                    response = self.client.commentThreads().list(
                        part='id,replies,snippet',
                        maxResults=100,
                        order='time',
                        videoId=video_id,
                        textFormat='plainText',
                        pageToken=next_page_token
                    ).execute()
                    results = response['items']
                    comments.extend(results)
                    num_result_on_page = response['pageInfo']['resultsPerPage']
                    if num_result_on_page < max_results \
                            or len(results) == 0 \
                            or 'nextPageToken' not in response:
                        end_flag = True
                    else:
                        next_page_token = response['nextPageToken']
                except Exception as e:
                    print(f'xxx Error! failed to get comments for video {video_id}')
                    print(str(e))
                    time.sleep(2 ** i)
        return comments

    # def get_video_ids(self, yt_id, page_token=None):
    #     """ Call the API's search().list method to get the list of video ids given a channel id.
    #     """
    #     # exponential back-off
    #     for i in range(0, 3):
    #         try:
    #             print('calling API...', page_token)
    #             response = self.client.search().list(channelId=yt_id, part='id', type='video',
    #                                                  maxResults=50, order='date', pageToken=page_token).execute()
    #             if response is not None and 'items' in response and len(response['items']) > 0:
    #                 print(len(response['items']), 'video are obtains')
    #                 print(response)
    #                 channel_videos = []
    #                 for res_json in response['items']:
    #                     # extract channel video ids
    #                     channel_videos.append(res_json['id']['videoId'])
    #
    #                 # recursively request next page
    #                 if 'nextPageToken' in response:
    #                     next_page_token = response['nextPageToken']
    #                     channel_videos.extend(self.get_video_ids(yt_id, page_token=next_page_token))
    #                 return channel_videos
    #         except Exception as e:
    #             print(str(e))
    #             time.sleep(2 ** i)
    #     return ''
