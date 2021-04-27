# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" Estimate the leanings of seed users by subscription lists.

Usage: python 5_estimate_user_leaning_subscription.py
Input data files: data/us_partisan.csv,
                  prediction/data/active_user_subscription.json.bz2
Output data file: prediction/5_subscription_seed_user_label_{threshold}.csv
Time: ~8M
"""

import up  # go to root folder

import json, bz2

from utils.helper import bias_metric, Timer


def main():
    timer = Timer()
    timer.start()

    channel_leaning_dict = {}
    with open('data/us_partisan.csv', 'r') as fin:
        # title, url, channel_title, channel_id, leaning, type, source, channel_description
        fin.readline()
        for line in fin:
            _, _, _, channel_id, leaning, _ = line.rstrip().split(',', 5)
            channel_leaning_dict[channel_id] = leaning

    print('{0} channels with known/polarized ideology'.format(len(channel_leaning_dict)))

    encoding = {'L': 0, 'R': 1}
    num_user = 0
    num_user_with_subscription = 0
    num_user_with_active_subscription = 0
    threshold = 5
    num_left_user = 0
    num_right_user = 0

    print('threshold', threshold)
    with open('prediction/5_subscription_seed_user_label_{0}.csv'.format(threshold), 'w') as fout:
        with bz2.BZ2File('prediction/data/active_user_subscription.json.bz2', 'r') as fin:
            for line in fin:
                line = line.decode('utf-8')
                user_json = json.loads(line.rstrip())
                user_id = user_json['channel_id']
                subscriptions = user_json['subscriptions']
                num_user += 1

                if len(subscriptions) > 0:
                    num_user_with_subscription += 1
                    subscribing_stats = [0] * 2
                    for subscription in subscriptions:
                        cid = subscription[0]
                        if cid in channel_leaning_dict:
                            if channel_leaning_dict[cid] != 'C':
                                subscribing_stats[encoding[channel_leaning_dict[cid]]] += 1
                    # subscribe to at least 5 channels with known leanings
                    if sum(subscribing_stats) >= threshold:
                        num_user_with_active_subscription += 1

                        left, right = subscribing_stats
                        bipartisan_bias = bias_metric(left, right)
                        if bipartisan_bias <= -0.9:
                            fout.write('{0},L,{1},{2}\n'.format(user_id, left, right))
                            num_left_user += 1
                        elif bipartisan_bias >= 0.9:
                            fout.write('{0},R,{1},{2}\n'.format(user_id, left, right))
                            num_right_user += 1

    print('we collect {0:,} users'.format(num_user))
    print('{0:,} ({1:.2f}%) users subscribe to at least one channel'.format(num_user_with_subscription, 100 * num_user_with_subscription / num_user))
    print('{0:,} ({1:.2f}%) users subscribe to at least {2} channel'.format(num_user_with_active_subscription, 100 * num_user_with_active_subscription / num_user, threshold))
    print('{0} left users, {1} right users'.format(num_left_user, num_right_user))

    timer.stop()


if __name__ == '__main__':
    main()
