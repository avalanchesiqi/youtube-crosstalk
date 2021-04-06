#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Fetching user description and subscriptions given a channel id.

Usage: python 12_scrape_youtube_featured_channels.py
Input data files: ../data/mbfc_usa_active_user.csv
Output data files: ../data/mbfc_usa_active_user_subscription.json.bz2
"""

import up  # go to root folder
import json, time

from utils.helper import Timer
from utils.crawlers import get_subscriptions_from_channel


def main():
    timer = Timer()
    timer.start()

    app_name = 'mbfc'

    input_filepath = 'data/{0}/{0}_ratings.csv'.format(app_name)
    output_filepath = 'data/{0}/MBFC_featured_channels.json'.format(app_name)

    with open(output_filepath, 'w') as fout:
        with open(input_filepath, 'r') as fin:
            fin.readline()
            for line in fin:
                _, channel_id, _, _, is_political = line.rstrip().rsplit(',', 4)
                if is_political == 'Y':
                    num_request = 0
                    found = False
                    print('get featured channels for channel {0}'.format(channel_id))
                    while num_request < 5:
                        try:
                            profile_json = get_subscriptions_from_channel(channel_id, target='featured')
                            found = True
                        except:
                            num_request += 1

                        if found:
                            if len(profile_json['featured_channels']) > 0:
                                fout.write('{0}\n'.format(json.dumps(profile_json)))
                                print(json.dumps(profile_json))
                                print('{0} featured channels are obtained for channel {1}\n'.format(len(profile_json['featured_channels']), channel_id))
                            time.sleep(1)
                            break

    timer.stop()


if __name__ == '__main__':
    main()
