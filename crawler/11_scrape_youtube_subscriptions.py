#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Fetching user description and subscriptions given a channel id.

Usage: python 11_scrape_youtube_subscriptions.py
Input data files: ../data/mbfc/to_crawl_users.csv
Output data files: ../data/mbfc/mbfc_usa_active_user_subscription.json.bz2
"""

import up  # go to root folder
import os, json, bz2, time

from utils.helper import Timer
from utils.crawlers import get_subscriptions_from_channel


def main():
    timer = Timer()
    timer.start()

    input_filepath = 'data/mbfc/to_crawl_users.csv'
    output_filepath = 'data/mbfc/active_user_subscription.json.bz2'

    visited_channel_set = set()
    if os.path.exists(output_filepath):
        with bz2.BZ2File(output_filepath, 'r') as fin:
            for line in fin:
                line = line.decode('utf-8')
                channel_id = json.loads(line.rstrip())['channel_id']
                visited_channel_set.add(channel_id)
    print('visited {0} channels in the past, continue...'.format(len(visited_channel_set)))

    num_user = len(visited_channel_set)
    with bz2.open(output_filepath, 'at') as fout:
        with open(input_filepath, 'r') as fin:
            for line in fin:
                user_id = line.rstrip().split(',')[0]
                if user_id not in visited_channel_set:
                    num_request = 0
                    found = False
                    print('get description and subscriptions for user {0}'.format(user_id))
                    while num_request < 5:
                        try:
                            profile_json = get_subscriptions_from_channel(user_id, target='subscription')
                            found = True
                        except:
                            num_request += 1

                        if found:
                            fout.write('{0}\n'.format(json.dumps(profile_json)))
                            num_user += 1
                            print('{0} subscriptions are obtained for user {1}: {2}\n'.format(len(profile_json['subscriptions']), num_user, user_id))
                            time.sleep(1)
                            break

    timer.stop()


if __name__ == '__main__':
    main()
