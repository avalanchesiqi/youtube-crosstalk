#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Fetching YouTube videos given a channel id.

Usage: python 7_fetch_youtube_videos_playlist.py
Input data files: ../data/mbfc/mbfc_ratings.csv
Output data files: ../data/mbfc/mbfc_video_ids_{date}.json
Time: ~1D for MBFC
"""

import up  # go to root folder
import os, json
from datetime import datetime

from utils.helper import Timer
from utils.crawlers import get_videos_from_playlist


def main():
    timer = Timer()
    timer.start()

    app_name = 'mbfc'

    current_date = datetime.now().strftime('%Y-%m-%d')
    input_filepath = 'data/{0}/{0}_ratings.csv'.format(app_name)
    output_filepath = 'data/{0}/{0}_video_ids_{1}.json'.format(app_name, current_date)
    visited_channel_set = set()
    if os.path.exists(output_filepath):
        with open(output_filepath, 'r') as fin:
            for line in fin:
                visited_channel_set.add(json.loads(line.rstrip())['channel_id'])
    print('visited {0} channels in the past, continue...'.format(len(visited_channel_set)))

    idx_media = len(visited_channel_set)
    with open(output_filepath, 'a') as fout:
        with open(input_filepath, 'r') as fin:
            fin.readline()
            for line in fin:
                channel_id = line.rstrip().split(',')[-1]
                if channel_id != '' and channel_id not in visited_channel_set:
                    print('get videos for media {0}'.format(channel_id))
                    upload_playlist = 'UU' + channel_id[2:]
                    num_fail = 0
                    while num_fail < 5:
                        try:
                            channel_video_ids = get_videos_from_playlist(upload_playlist)
                            break
                        except:
                            num_fail += 1

                    fout.write('{0}\n'.format(json.dumps({'channel_id': channel_id, 'playlist': channel_video_ids})))
                    visited_channel_set.add(channel_id)
                    idx_media += 1
                    print('{0} video ids are obtained for media {1}: {2}\n'.format(len(channel_video_ids), idx_media, channel_id))

    timer.stop()


if __name__ == '__main__':
    main()
