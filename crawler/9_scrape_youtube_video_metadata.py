#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Fetching YouTube video metadata given a video id.
Feature set: vid, title, channel_id, keywords, category, description, duration, publish_date, snapshot_pt_time, view_count, num_like, num_dislike, transcript, num_comment, comment_list

Usage: python 9_scrape_youtube_video_metadata.py
Input data files: data/mbfc/to_crawl_vid.csv
Output data files: data/mbfc/crawled_video_metadata.json
Time: ~1D
"""

import up  # go to root folder

import os, time, json, requests, re, random, bz2, codecs
from datetime import datetime
from pytz import timezone
from html import unescape
from xml.etree import ElementTree

from utils.helper import Timer
from utils.crawlers import USER_AGENT_LIST, YOUTUBE_VIDEO_URL, find_value, search_dict
from utils.yt_comments import download_comments_top, download_comments_time

HTML_TAG_REGEX = re.compile(r'<[^>]*>', re.IGNORECASE)
PT_TIMEZONE = timezone('US/Pacific')


def parse_transcript(plain_data):
    return [{'text': re.sub(HTML_TAG_REGEX, '', unescape(xml_element.text)),
             'start': float(xml_element.attrib['start']),
             'duration': float(xml_element.attrib.get('dur', '0.0'))}
            for xml_element in ElementTree.fromstring(plain_data) if xml_element.text is not None]


def get_video_metadata(video_id):
    timer = Timer()
    timer.start()

    print('>>> now crawling video_id: {0}'.format(video_id))

    num_block = 0
    num_fail = 0
    while True:
        if num_block > 3:
            raise Exception('xxx error, IP blocked, STOP the program...')

        if num_fail > 5:
            print('xxx error, too many fails for video {0}'.format(video_id))
            return {}

        session = requests.Session()
        session.headers['User-Agent'] = random.choice(USER_AGENT_LIST)

        response = session.get(YOUTUBE_VIDEO_URL.format(video_id=video_id))
        # too many requests, IP is banned by YouTube
        if response.status_code == 429:
            print('xxx error, too many requests, sleep for 5 minutes, iteration: {0}'.format(num_block))
            num_block += 1
            time.sleep(300)
            continue
        if response is not None:
            html = response.text

            prefix_player = 'window["ytInitialPlayerResponse"] = '
            suffix_player = '\n'
            if prefix_player not in html:
                prefix_player = 'var ytInitialPlayerResponse = '
                suffix_player = ';var'
            prefix_data = 'window["ytInitialData"] = '
            suffix_data = '\n'
            if prefix_data not in html:
                prefix_data = 'var ytInitialData = '
                suffix_data = ';</'

            try:
                initial_player_response = json.loads(find_value(html, prefix_player, 0, suffix_player).rstrip(';'))
                # print(json.dumps(initial_player_response))
                initial_data = json.loads(find_value(html, prefix_data, 0, suffix_data).rstrip(';'))
                # print(json.dumps(initial_data))
            except:
                num_fail += 1
                continue

            if 'videoDetails' not in initial_player_response \
                    or 'microformat' not in initial_player_response \
                    or 'playerMicroformatRenderer' not in initial_player_response['microformat']:
                print('xxx private or unavailable video {0}'.format(video_id))
                return {}

            video_details = initial_player_response['videoDetails']
            microformat_renderer = initial_player_response['microformat']['playerMicroformatRenderer']

            title = video_details['title']
            channel_id = video_details['channelId']
            category = microformat_renderer.get('category', '')
            print('>>> video_id: {0}, category: {1}'.format(video_id, category))

            keywords = video_details.get('keywords', [])
            description = video_details['shortDescription']
            duration = video_details['lengthSeconds']
            publish_date = microformat_renderer['publishDate']
            snapshot_pt_time = datetime.now(PT_TIMEZONE).strftime('%Y-%m-%d-%H')
            view_count = microformat_renderer.get('viewCount', 0)
            is_streamed = video_details['isLiveContent']

            num_like = 0
            num_dislike = 0
            for toggle_button_renderer in search_dict(initial_data, 'toggleButtonRenderer'):
                icon_type = next(search_dict(toggle_button_renderer, 'iconType'), '')
                if icon_type == 'LIKE':
                    default_text = next(search_dict(toggle_button_renderer, 'defaultText'), {})
                    if len(default_text) > 0:
                        try:
                            num_like = int(default_text['accessibility']['accessibilityData']['label'].split()[0].replace(',', ''))
                        except:
                            pass
                elif icon_type == 'DISLIKE':
                    default_text = next(search_dict(toggle_button_renderer, 'defaultText'), {})
                    if len(default_text) > 0:
                        try:
                            num_dislike = int(default_text['accessibility']['accessibilityData']['label'].split()[0].replace(',', ''))
                        except:
                            pass

            ret_json = {'vid': video_id, 'title': title, 'channel_id': channel_id, 'category': category,
                        'keywords': keywords, 'description': description, 'duration': duration,
                        'publish_date': publish_date, 'snapshot_pt_time': snapshot_pt_time, 'is_streamed': is_streamed,
                        'view_count': view_count, 'num_like': num_like, 'num_dislike': num_dislike,
                        'lang': 'NA', 'transcript': 'NA', 'num_comment': 'NA', 'comment_list': 'NA', 'top_comment_list': 'NA'}

            # early return if non-political video
            if category not in ['News & Politics', 'Nonprofits & Activism', 'People & Blogs', 'Education', 'Entertainment', 'Comedy']:
                print('xxx non-political video {0}, category: {1}\n'.format(video_id, category))
                return ret_json
            # print('>>> Step 1: finish getting the metadata via parsing the html page...')

            # 2. get video English transcript
            transcript_response = ''
            caption_tracks = next(search_dict(initial_player_response, 'captionTracks'), [])
            for caption_track in caption_tracks:
                if caption_track['languageCode'] == 'en':
                    if 'kind' in caption_track and caption_track['kind'] == 'asr':
                        transcript_url = caption_track['baseUrl']
                        transcript_response = session.get(transcript_url)
                        break
                    else:
                        transcript_url = caption_track['baseUrl']
                        transcript_response = session.get(transcript_url)
                        break

            if transcript_response != '':
                eng_subtitle = ''
                for segment in parse_transcript(transcript_response.text):
                    if 'text' in segment:
                        seg_text = segment['text'].lower()
                        eng_subtitle += seg_text
                        eng_subtitle += ' '
                ret_json['transcript'] = eng_subtitle
            # print('>>> Step 2: finish getting video English transcript...')

            # 3. get video comments via yt_comments package
            session_token = codecs.decode(find_value(html, 'XSRF_TOKEN', 3), 'unicode_escape')
            ncd = next(search_dict(initial_data, 'nextContinuationData'), None)
            try:
                if is_streamed:
                    comment_list, num_request = download_comments_top(session, session_token, ncd, top=False)
                    if isinstance(comment_list, list):
                        ret_json['num_comment'] = len(comment_list)
                        ret_json['comment_list'] = comment_list
                        ret_json['num_request'] = num_request
                        print('>>> {0} comments are downloaded, {1} requests are sent'.format(len(comment_list), num_request))
                else:
                    comment_list, num_request = download_comments_time(session, video_id, session_token)
                    top_comment_list, num_request2 = download_comments_top(session, session_token, ncd, top=True)
                    if isinstance(comment_list, list):
                        ret_json['num_comment'] = len(comment_list)
                        ret_json['comment_list'] = comment_list
                        ret_json['top_comment_list'] = top_comment_list
                        ret_json['num_request'] = num_request + num_request2
                        print('>>> {0} comments, {1} top comments are downloaded, {2} requests are sent'.format(len(comment_list), len(top_comment_list), num_request))
            except Exception as e:
                if 'Comments are turned off' in str(e):
                    print('>>> Comments are turned off')
                else:
                    print('xxx exception in downloading the comments,', str(e))
                pass
            # print('>>> Step 3: finish getting video comments...')

            timer.stop()

            time.sleep(5)
            return ret_json
    return {}


def main():
    timer = Timer()
    timer.start()

    input_filepath = 'data/mbfc/to_crawl_vid.txt'
    output_filepath = 'data/mbfc/MBFC_video_metadata.json.bz2'

    visited_video_set = set()
    if os.path.exists(output_filepath):
        with bz2.BZ2File(output_filepath, mode='r') as fin:
            for line in fin:
                video_json = json.loads(line.rstrip())
                if 'vid' in video_json:
                    visited_video_set.add(video_json['vid'])
    print('visited {0} videos in the past, continue...'.format(len(visited_video_set)))

    num_video = len(visited_video_set)
    total_num_request = 0
    with bz2.open(output_filepath, 'at') as fout:
        with open(input_filepath, 'r') as fin:
            for line in fin:
                video_id = line.rstrip()
                if video_id not in visited_video_set:
                    try:
                        video_metadata = get_video_metadata(video_id)
                        total_num_request += video_metadata.pop('num_request', 0)
                        if len(video_metadata) > 0:
                            visited_video_set.add(video_id)
                            fout.write('{0}\n'.format(json.dumps(video_metadata)))
                            num_video += 1
                        else:
                            print('xxx error, failed in crawling metadata for video {0}'.format(video_id))
                    except Exception as e:
                        print(str(e))
                        break
                    print('>>> so far crawled {0} videos, {1} requests are sent'.format(num_video, total_num_request))

    print('>>> reach file end!')
    timer.stop()


if __name__ == '__main__':
    main()
