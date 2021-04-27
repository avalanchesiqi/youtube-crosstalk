# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" Estimate user political leanings based on hashtag usages in user title and profile.

Usage: python 1_estimate_user_leaning_profile_hashtag.py
Input data files: prediction/data/profile_left_hashtags.csv,
                  prediction/data/profile_right_hashtags.csv,
                  prediction/data/profile_hashtag_list.tsv.bz2
Output data file: prediction/1_profile_seed_user_label.csv
Time: ~10S
"""

import up  # go to root folder

import bz2
from utils.helper import Timer


def main():
    timer = Timer()
    timer.start()

    left_hashtags = set()
    right_hashtags = set()
    with open('prediction/data/profile_left_hashtags.csv', 'r') as fin:
        for line in fin:
            hashtag, _ = line.rstrip().split(',')
            left_hashtags.add(hashtag)

    with open('prediction/data/profile_right_hashtags.csv', 'r') as fin:
        for line in fin:
            hashtag, _ = line.rstrip().split(',')
            right_hashtags.add(hashtag)

    print('{0} profile seed left hashtags, {1} right hashtags'.format(len(left_hashtags), len(right_hashtags)))

    predicted_left_cnt = 0
    predicted_right_cnt = 0
    conflict_cnt = 0
    with open('prediction/1_profile_seed_user_label.csv', 'w') as fout:
        with bz2.BZ2File('prediction/data/profile_hashtag_list.tsv.bz2', 'r') as fin:
            for line in fin:
                line = line.decode('utf-8')
                user_id, hashtag_stats = line.rstrip().split('\t', 1)
                hashtag_freq_list = hashtag_stats.split()
                hashtag_set = {x.split(',')[0] for x in hashtag_freq_list if len(x.split(',')[0]) > 1}

                used_left_set = set()
                used_right_set = set()
                for hashtag in hashtag_set:
                    if hashtag in left_hashtags:
                        used_left_set.add(hashtag)
                    elif hashtag in right_hashtags:
                        used_right_set.add(hashtag)

                num_left_hashtags = len(used_left_set)
                num_right_hashtags = len(used_right_set)
                if num_left_hashtags > 0 or num_right_hashtags > 0:
                    if num_right_hashtags == 0:
                        predicted_left_cnt += 1
                        fout.write('{0},{1}\n'.format(user_id, 'L'))
                    elif num_left_hashtags == 0:
                        predicted_right_cnt += 1
                        fout.write('{0},{1}\n'.format(user_id, 'R'))
                    else:
                        conflict_cnt += 1
                        print('{0},{1},{2}'.format(user_id, num_left_hashtags, num_right_hashtags))
                        print(used_left_set)
                        print(used_right_set)
                        print('=' * 79)

    print('>>> predicted {0} left users'.format(predicted_left_cnt))
    print('>>> predicted {0} right users'.format(predicted_right_cnt))
    print('>>> in total, predicted {0} users'.format(predicted_left_cnt + predicted_right_cnt))
    print('>>> {0} conflicted user by profile'.format(conflict_cnt))

    timer.stop()


if __name__ == '__main__':
    main()
