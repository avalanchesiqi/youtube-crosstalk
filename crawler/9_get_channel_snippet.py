#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Getting YouTube channel snippet, statistics given a YouTube channel id.

Usage: python 9_get_channel_snippet.py
Input data files: ../data/mbfc/mbfc_video_ids_jan_aug.json
Output data files: ../data/mbfc_video_ids_jan_aug_profile.json
Time: 5M for MBFC
"""

import up  # go to root folder
import json, re

from utils.helper import Timer
from utils.crawlers import YTCrawler


def remove_non_ascii(text):
    return re.sub(r'[^\x00-\x7F]', ' ', text)


def main():
    timer = Timer()
    timer.start()

    d_key = 'Set your own developer key!'
    parts = 'id,snippet,statistics'

    yt_crawler = YTCrawler()
    yt_crawler.set_key(d_key)

    app_name = 'mbfc'

    num_crawled = 0
    channel_profile_dict = {}
    with open('data/{0}/{0}_video_ids_jan_aug_profile.json'.format(app_name), 'w') as fout:
        with open('data/{0}/{0}_video_ids_jan_aug.json'.format(app_name),
                  'r') as fin:
            for line in fin:
                channel_json = json.loads(line.rstrip())
                channel_id = channel_json['channel_id']
                num_video = channel_json['num_video']
                yt_snippet_dict = yt_crawler.get_channel_snippet(channel_id, parts)
                ret_json = {'channel_id': channel_id, 'num_video': num_video}
                ret_json.update(yt_snippet_dict)
                channel_profile_dict[channel_id] = ret_json
                num_crawled += 1
                print('>>> crawled {0} media sites'.format(num_crawled))
                fout.write('{0}\n'.format(json.dumps(ret_json)))

    # with open('../data/mbfc_video_ids_jan_sep_profile.json', 'r') as fin:
    #     for line in fin:
    #         channel_json = json.loads(line.rstrip())
    #         channel_profile_dict[channel_json['channel_id']] = channel_json

    with open('../data/mbfc_ratings_new.csv', 'w') as fout:
        fout.write('title,country,mbfc_page,bias_raw,factual,label,url,channel_id,publish_at_2020?,num_video,channel_title,channel_country,channel_description\n')
        with open('../data/mbfc_ratings.csv', 'r', encoding='windows-1252') as fin:
            fin.readline()
            for line in fin:
                channel_id = line.rstrip().split(',')[-1]
                try:
                    if channel_id != '':
                        if channel_id in channel_profile_dict:
                            fout.write('{0},{1},{2},{3},{4},{5}\n'.format(line.rstrip(), 'Y',
                                                                          channel_profile_dict[channel_id]['num_video'],
                                                                          remove_non_ascii(channel_profile_dict[channel_id]['yt_title']).replace(',', ' ').replace('\r', ' ').replace('\n', ' '),
                                                                          channel_profile_dict[channel_id]['yt_country'],
                                                                          remove_non_ascii(channel_profile_dict[channel_id]['yt_description']).replace(',', ' ').replace('\r', ' ').replace('\n', ' ')))
                        else:
                            fout.write('{0},{1},,,,\n'.format(line.rstrip(), 'N'))
                    else:
                        fout.write('{0},,,,,\n'.format(line.rstrip()))
                except Exception as e:
                    print(str(e))
                    print(line)

    timer.stop()


if __name__ == '__main__':
    main()
