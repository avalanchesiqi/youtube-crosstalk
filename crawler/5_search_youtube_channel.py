#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Searching for the unresolved YouTube channels by searching site title on YouTube.

Usage: python 5_search_youtube_channel.py
Input data files: .data/mbfc/mbfc_ratings_v4.csv
Output data files: data/mbfc/mbfc_ratings_v5.csv
Time: 20M for MBFC
"""

import up  # go to root folder

import time, requests, random, json

from utils.helper import Timer
from utils.crawlers import USER_AGENT_LIST, YOUTUBE_CHANNEL_ABOUT
from utils.crawlers import find_value, search_dict, get_search_request, match_links_on_youtube_page


def main():
    timer = Timer()
    timer.start()

    app_name = 'mbfc'

    num_hit_youtube = 0
    num_fail_youtube = 0
    num_search = 0

    with open('data/{0}/{0}_ratings_v5.csv'.format(app_name), 'w') as fout:
        with open('data/{0}/{0}_ratings_v4.csv'.format(app_name), 'r') as fin:
            fout.write(fin.readline())
            for line in fin:
                title, tail = line.rstrip().split(',', 1)
                middle, website_url, tw_handle, tw_sim, yt_id, yt_user = tail.rsplit(',', 5)
                if yt_id != '' or yt_user != '':
                    fout.write(line)
                else:
                    # searching YouTube search bar for youtube channels if we cannot find it on webpage
                    print('===============')
                    num_search += 1
                    num_search_results = 0
                    search_results = []
                    for _ in range(5):
                        if num_search_results == 0:
                            print('sent a request to YouTube search bar with title "{0}"...'.format(title))
                            search_request = get_search_request(title)
                            print(search_request)
                            try:
                                search_response = requests.get(search_request,
                                                               headers={'User-Agent': random.choice(USER_AGENT_LIST)})
                            except Exception as e:
                                print(str(e))
                                search_response = requests.get(search_request)
                            time.sleep(1)

                            if search_response:
                                html = search_response.text

                                try:
                                    initial_data = json.loads(find_value(html, 'window["ytInitialData"] = ', 0, '\n').rstrip(';'))
                                    # print(json.dumps(initial_data))
                                except:
                                    continue

                                # get the first 10 YouTube channels
                                search_results = list(search_dict(initial_data, 'channelRenderer'))[:10]
                                num_search_results = len(search_results)
                                print('find {0} search results'.format(num_search_results))

                    found_match = False
                    for search_result in search_results:
                        channel_title = search_result['title']['simpleText']
                        channel_id = search_result['navigationEndpoint']['browseEndpoint']['browseId']
                        print(channel_title, channel_id)
                        if channel_title != '':
                            print(YOUTUBE_CHANNEL_ABOUT.format(channel_id=channel_id))
                            channel_response = requests.get(YOUTUBE_CHANNEL_ABOUT.format(channel_id=channel_id))
                            time.sleep(1)
                            if match_links_on_youtube_page(channel_response, website_url, tw_handle):
                                found_match = True
                                yt_id = channel_id
                                break

                    if found_match:
                        num_hit_youtube += 1
                        print('success index {0}/{4}: {1}, {2}, {3}'.format(num_hit_youtube, title, yt_id, '', num_search))
                        fout.write('{0},{1},{2},{3},{4},{5},{6}\n'.format(title, middle, website_url, tw_handle, tw_sim, yt_id, ''))
                    else:
                        num_fail_youtube += 1
                        print('fail index {0}/{2}: {1}'.format(num_fail_youtube, title, num_search))
                        fout.write(line)

    timer.stop()


if __name__ == '__main__':
    main()
