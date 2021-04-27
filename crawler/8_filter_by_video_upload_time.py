#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Keeping video ids if they are uploaded between 2020-01-01 and 2020-08-31.

Usage: python 8_filter_by_video_upload_time.py
Input data files: data/mbfc/mbfc_video_ids_2020-09-27.json
Output data files: data/mbfc/mbfc_video_ids_jan_aug.json
Time: ~6H
"""

import up  # go to root folder

import os, time, json, requests, random

from utils.helper import Timer
from utils.crawlers import USER_AGENT_LIST, YOUTUBE_VIDEO_URL, find_value


def get_upload_time(video_id):
    num_block = 0
    num_fail = 0
    while True:
        if num_block > 3:
            return 'xxx error, received 20x 429 code. STOP the program...'

        if num_fail > 5:
            print('xxx error, failed in crawling metdata for video {0}'.format(video_id))
            return ''

        session = requests.Session()
        session.headers['User-Agent'] = random.choice(USER_AGENT_LIST)

        response = session.get(YOUTUBE_VIDEO_URL.format(video_id=video_id))
        # too many requests, IP is banned by YouTube
        if response.status_code == 429:
            print('xxx error, too many requests, IP is banned, sleep for 5 minutes, iteration: {0}'.format(num_block))
            num_block += 1
            time.sleep(300)
            continue
        if response is not None:
            html = response.text

            try:
                initial_player_response = json.loads(find_value(html, 'window["ytInitialPlayerResponse"] = ', 0, '\n').rstrip(';'))
                # print(json.dumps(initial_player_response))
            except:
                num_fail += 1
                continue

            if 'microformat' not in initial_player_response or 'playerMicroformatRenderer' not in initial_player_response['microformat']:
                print('xxx private or unavailable video {0}'.format(video_id))
                return ''

            microformat_renderer = initial_player_response['microformat']['playerMicroformatRenderer']
            publish_date = microformat_renderer['publishDate']
            time.sleep(1)
            return publish_date
    return ''


def main():
    timer = Timer()
    timer.start()

    app_name = 'mbfc'

    START_DATE = '2020-01-01'
    END_DATE = '2020-08-31'
    input_filepath = 'data/{0}/{0}_video_ids_2020-09-27.json'.format(app_name)
    output_filepath = 'data/{0}/{0}_video_ids_jan_aug.json'.format(app_name)

    visited_channel_list = []
    if os.path.exists(output_filepath):
        with open(output_filepath, 'r') as fin:
            for line in fin:
                channel_json = json.loads(line.rstrip())
                visited_channel_list.append(channel_json['channel_id'])

    idx_media = len(visited_channel_list)
    print('has crawled {0} videos'.format(idx_media))
    with open(output_filepath, 'a') as fout:
        with open(input_filepath, 'r') as fin:
            for line in fin:
                channel_videos = json.loads(line.rstrip())
                channel_id = channel_videos['channel_id']
                if channel_id not in visited_channel_list:
                    visited_channel_list.append(channel_id)
                    idx_media += 1

                    print('channel idx {0}, id {1}'.format(idx_media, channel_id))
                    video_ids = channel_videos['playlist'][::-1]
                    num_channel_video = len(video_ids)
                    if num_channel_video > 0:
                        # binary search to keep videos uploaded between Jan 01, 2020 and Jul 31, 2020
                        # boundary check
                        earliest_idx = 0
                        earliest_date = get_upload_time(video_ids[earliest_idx])
                        while earliest_date == '':
                            earliest_idx += 1
                            earliest_date = get_upload_time(video_ids[earliest_idx])
                        if earliest_date > END_DATE:
                            continue
                        find_left = False
                        if earliest_date > START_DATE:
                            left_bound_idx = earliest_idx
                            left_bound_date = earliest_date
                            print('>>> find left bound idx in boundary', left_bound_idx, left_bound_date)
                            find_left = True

                        latest_idx = num_channel_video - 1
                        latest_date = get_upload_time(video_ids[latest_idx])
                        while latest_date == '':
                            latest_idx -= 1
                            latest_date = get_upload_time(video_ids[latest_idx])
                        if latest_date < START_DATE:
                            continue
                        find_right = False
                        if latest_date < END_DATE:
                            right_bound_idx = latest_idx
                            right_bound_date = latest_date
                            print('>>> find right bound idx in boundary', right_bound_idx, right_bound_date)
                            find_right = True

                        # find the left_bound_idx, earliest date
                        if not find_left:
                            curr_left_idx = earliest_idx
                            curr_right_idx = latest_idx
                            while not (find_left or (curr_left_idx == curr_right_idx) or (curr_left_idx + 1 == curr_right_idx)):
                                curr_mid_idx = (curr_left_idx + curr_right_idx) // 2
                                curr_mid_date = get_upload_time(video_ids[curr_mid_idx])
                                print('middle idx: {0}, video id: {1}, upload time: {2}'.format(curr_mid_idx, video_ids[curr_mid_idx], curr_mid_date))
                                if curr_mid_date == '':
                                    curr_left_idx += 1
                                else:
                                    if curr_mid_date < START_DATE:
                                        curr_left_idx = curr_mid_idx
                                    else:
                                        curr_right_idx = curr_mid_idx
                                    print('left bound update', curr_left_idx, curr_right_idx)
                            left_bound_idx = curr_right_idx
                            left_bound_date = get_upload_time(video_ids[curr_right_idx])
                            if left_bound_date > END_DATE:
                                continue
                            print('>>> find left bound idx', left_bound_idx, left_bound_date, get_upload_time(video_ids[left_bound_idx - 1]))

                        # find the right_bound_idx, latest date
                        if not find_right:
                            curr_left_idx = left_bound_idx
                            curr_right_idx = latest_idx
                            while not (find_right or (curr_left_idx == curr_right_idx) or (curr_left_idx + 1 == curr_right_idx)):
                                curr_mid_idx = (curr_left_idx + curr_right_idx) // 2
                                curr_mid_date = get_upload_time(video_ids[curr_mid_idx])
                                print('middle idx: {0}, video id: {1}, upload time: {2}'.format(curr_mid_idx, video_ids[curr_mid_idx], curr_mid_date))
                                if curr_mid_date == '':
                                    curr_right_idx = curr_right_idx - 1
                                else:
                                    if curr_mid_date > END_DATE:
                                        curr_right_idx = curr_mid_idx
                                    else:
                                        curr_left_idx = curr_mid_idx
                                    print('right bound update', curr_left_idx, curr_right_idx)
                            right_bound_idx = curr_left_idx
                            right_bound_date = get_upload_time(video_ids[curr_left_idx])
                            if right_bound_date < START_DATE:
                                continue
                            print('>>> find right bound idx', right_bound_idx, right_bound_date, get_upload_time(video_ids[right_bound_idx + 1]))

                        print('>>> find {0} videos'.format(right_bound_idx + 1 - left_bound_idx), left_bound_idx, right_bound_idx, left_bound_date, right_bound_date)
                        fout.write('{0}\n'.format(json.dumps({'channel_id': channel_id,
                                                              'start_date': left_bound_date,
                                                              'end_date': right_bound_date,
                                                              'num_video': right_bound_idx + 1 - left_bound_idx,
                                                              'video_ids': video_ids[left_bound_idx: right_bound_idx + 1]})))
                        print('='*60)
                        print()

    timer.stop()


if __name__ == '__main__':
    main()
