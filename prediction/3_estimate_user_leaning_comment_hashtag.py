# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" Estimate user political leanings based on political hashtags in user comments and profiles.

Usage: python 3_estimate_user_leaning_comment_hashtag.py
Input data files: prediction/data/comment_seed_left_hashtags.csv,
                  prediction/data/comment_seed_right_hashtags.csv,
                  prediction/data/profile_left_hashtags.csv,
                  prediction/data/profile_right_hashtags.csv,
                  prediction/data/comment_hashtag_list.tsv.bz2
Output data file: prediction/3_comment_expanded_left_hashtags.csv,
                  prediction/3_comment_expanded_right_hashtags.csv,
                  prediction/3_comment_seed_user_label_{threshold}.csv
Time: ~1M
"""

import up  # go to root folder

import bz2

from utils.helper import bias_metric, Timer


def propagate_hashtag_to_user(user_hashtag_graph_filename, left_hashtags, right_hashtags, threshold, verbose=False):
    user_label_dict = {}
    num_estimated_left_user = 0
    num_estimated_right_user = 0
    with bz2.BZ2File(user_hashtag_graph_filename, 'r') as fin:
        for line in fin:
            line = line.decode('utf-8')
            user_id, hashtag_stats = line.rstrip().split('\t', 1)
            hashtag_freq_list = hashtag_stats.split()
            hashtag_freq_dict = {x.split(',')[0]: int(x.split(',')[1]) for x in hashtag_freq_list if len(x.split(',')[0]) > 1}

            num_left_hashtag = 0
            num_right_hashtag = 0

            for hashtag, freq in hashtag_freq_dict.items():
                if hashtag in left_hashtags:
                    num_left_hashtag += freq
                elif hashtag in right_hashtags:
                    num_right_hashtag += freq

            num_total_freq = num_left_hashtag + num_right_hashtag
            if num_total_freq >= threshold:
                bipartisan_bias = bias_metric(num_left_hashtag, num_right_hashtag)
                if bipartisan_bias <= -0.9:
                    num_estimated_left_user += 1
                    if verbose:
                        user_label_dict[user_id] = 'L,{0},{1}'.format(num_left_hashtag, num_right_hashtag)
                    else:
                        user_label_dict[user_id] = 'L'
                elif bipartisan_bias >= 0.9:
                    num_estimated_right_user += 1
                    if verbose:
                        user_label_dict[user_id] = 'R,{0},{1}'.format(num_left_hashtag, num_right_hashtag)
                    else:
                        user_label_dict[user_id] = 'R'

    print('estimate {0:,} left users and {1:,} right users'.format(num_estimated_left_user, num_estimated_right_user))
    return user_label_dict


def propagate_user_to_hashtag(user_hashtag_graph_filename, user_label_dict, left_hashtags, right_hashtags, threshold):
    unknown_hashtags = set()
    with bz2.BZ2File(user_hashtag_graph_filename, 'r') as fin:
        for line in fin:
            line = line.decode('utf-8')
            user_id, hashtag_stats = line.rstrip().split('\t', 1)
            hashtag_freq_list = hashtag_stats.split()
            hashtag_set = {x.split(',')[0] for x in hashtag_freq_list if len(x.split(',')[0]) > 1}
            if user_id in user_label_dict:
                unknown_hashtags.update(hashtag_set)
    unknown_hashtags = unknown_hashtags - left_hashtags - right_hashtags
    print('>>> {0:,} new unknown hashtags'.format(len(unknown_hashtags)))

    left_hashtag_stats = {hashtag: [0, 0, 0] for hashtag in left_hashtags}
    right_hashtag_stats = {hashtag: [0, 0, 0] for hashtag in right_hashtags}
    unknown_hashtag_stats = {hashtag: [0, 0, 0] for hashtag in unknown_hashtags}

    with bz2.BZ2File(user_hashtag_graph_filename, 'r') as fin:
        for line in fin:
            line = line.decode('utf-8')
            user_id, hashtag_stats = line.rstrip().split('\t', 1)
            hashtag_freq_list = hashtag_stats.split()
            hashtag_set = {x.split(',')[0] for x in hashtag_freq_list if len(x.split(',')[0]) > 1}
            if user_id in user_label_dict:
                unknown_hashtags.update(hashtag_set)
                if user_label_dict[user_id] == 'L':
                    for hashtag in hashtag_set:
                        if hashtag in left_hashtags:
                            left_hashtag_stats[hashtag][0] += 1
                        elif hashtag in right_hashtags:
                            right_hashtag_stats[hashtag][0] += 1
                        elif hashtag in unknown_hashtags:
                            unknown_hashtag_stats[hashtag][0] += 1
                else:
                    for hashtag in hashtag_set:
                        if hashtag in left_hashtags:
                            left_hashtag_stats[hashtag][2] += 1
                        elif hashtag in right_hashtags:
                            right_hashtag_stats[hashtag][2] += 1
                        elif hashtag in unknown_hashtags:
                            unknown_hashtag_stats[hashtag][2] += 1
            else:
                for hashtag in hashtag_set:
                    if hashtag in left_hashtags:
                        left_hashtag_stats[hashtag][1] += 1
                    elif hashtag in right_hashtags:
                        right_hashtag_stats[hashtag][1] += 1
                    elif hashtag in unknown_hashtags:
                        unknown_hashtag_stats[hashtag][1] += 1

    print('>>> sanity check existing hashtags')
    for hashtag in left_hashtag_stats:
        num_used_by_left_users, num_used_by_unknown_users, num_used_by_right_users = left_hashtag_stats[hashtag]
        if (num_used_by_left_users + num_used_by_right_users) > 0:
            bipartisan_bias = bias_metric(num_used_by_left_users, num_used_by_right_users)
            if bipartisan_bias > -0.9:
                print(hashtag, '{0:.2f}'.format(bipartisan_bias), left_hashtag_stats[hashtag])

    print('=' * 79)
    for hashtag in right_hashtag_stats:
        num_used_by_left_users, num_used_by_unknown_users, num_used_by_right_users = right_hashtag_stats[hashtag]
        if (num_used_by_left_users + num_used_by_right_users) > 0:
            bipartisan_bias = bias_metric(num_used_by_left_users, num_used_by_right_users)
            if bipartisan_bias < 0.9:
                print(hashtag, '{0:.2f}'.format(bipartisan_bias), right_hashtag_stats[hashtag])

    expanded_left_hashtags = set()
    expanded_right_hashtags = set()
    for hashtag in unknown_hashtag_stats:
        num_used_by_left_users, num_used_by_unknown_users, num_used_by_right_users = unknown_hashtag_stats[hashtag]
        if (num_used_by_left_users + num_used_by_right_users) >= threshold:
            bipartisan_bias = bias_metric(num_used_by_left_users, num_used_by_right_users)
            if bipartisan_bias <= -0.9:
                expanded_left_hashtags.add(hashtag)
            elif bipartisan_bias >= 0.9:
                expanded_right_hashtags.add(hashtag)

    finish_flag = False
    print('\nexpand {0:,} left hashtags and {1:,} right hashtags'.format(len(expanded_left_hashtags), len(expanded_right_hashtags)))
    if len(expanded_left_hashtags) == 0 and len(expanded_right_hashtags) == 0:
        finish_flag = True
    print('>>> expanded sample left')
    sample_left = list(expanded_left_hashtags)[:10]
    for hashtag in sample_left:
        num_used_by_left_users, num_used_by_unknown_users, num_used_by_right_users = unknown_hashtag_stats[hashtag]
        bipartisan_bias = bias_metric(num_used_by_left_users, num_used_by_right_users)
        print(hashtag, bipartisan_bias, unknown_hashtag_stats[hashtag])
    print('>>> expanded sample right')
    sample_right = list(expanded_right_hashtags)[:10]
    for hashtag in sample_right:
        num_used_by_left_users, num_used_by_unknown_users, num_used_by_right_users = unknown_hashtag_stats[hashtag]
        bipartisan_bias = bias_metric(num_used_by_left_users, num_used_by_right_users)
        print(hashtag, bipartisan_bias, unknown_hashtag_stats[hashtag])

    return expanded_left_hashtags.union(left_hashtags), expanded_right_hashtags.union(right_hashtags), finish_flag


def main():
    timer = Timer()
    timer.start()

    # load seed hashtags
    left_hashtags = set()
    with open('prediction/data/comment_seed_left_hashtags.csv', 'r') as fin:
        for line in fin:
            hashtag = line.rstrip()
            left_hashtags.add(hashtag)
    with open('prediction/data/profile_left_hashtags.csv', 'r') as fin:
        for line in fin:
            hashtag, _ = line.rstrip().split(',')
            left_hashtags.add(hashtag)

    right_hashtags = set()
    with open('prediction/data/comment_seed_right_hashtags.csv', 'r') as fin:
        for line in fin:
            hashtag = line.rstrip()
            right_hashtags.add(hashtag)
    with open('prediction/data/profile_right_hashtags.csv', 'r') as fin:
        for line in fin:
            hashtag, _ = line.rstrip().split(',')
            right_hashtags.add(hashtag)

    print('>>> {0} seed left hashtags'.format(len(left_hashtags)))
    print('>>> {0} seed right hashtags'.format(len(right_hashtags)))
    assert len(left_hashtags.intersection(right_hashtags)) == 0

    threshold = 5
    num_iter = 0
    finish_flag = False
    user_hashtag_graph_filename = 'prediction/data/comment_hashtag_list.tsv.bz2'

    while not finish_flag:
        print('>>> in iteration {0}'.format(num_iter + 1))
        user_label_dict = propagate_hashtag_to_user(user_hashtag_graph_filename, left_hashtags, right_hashtags, threshold)
        left_hashtags, right_hashtags, finish_flag = propagate_user_to_hashtag(user_hashtag_graph_filename, user_label_dict, left_hashtags, right_hashtags, threshold)
        print('>>> {0} left hashtags'.format(len(left_hashtags)))
        print('>>> {0} right hashtags'.format(len(right_hashtags)))
        print('=' * 79)
        num_iter += 1

    with open('prediction/3_comment_expanded_left_hashtags.csv', 'w', encoding='utf-8') as fout:
        for hashtag in left_hashtags:
            fout.write('{0}\n'.format(hashtag))

    with open('prediction/3_comment_expanded_right_hashtags.csv', 'w', encoding='utf-8') as fout:
        for hashtag in right_hashtags:
            fout.write('{0}\n'.format(hashtag))

    user_label_dict = propagate_hashtag_to_user(user_hashtag_graph_filename, left_hashtags, right_hashtags, threshold, verbose=False)
    with open('prediction/3_comment_seed_user_label_{0}.csv'.format(threshold), 'w') as fout:
        for user_id, label in user_label_dict.items():
            fout.write('{0},{1}\n'.format(user_id, label))

    timer.stop()


if __name__ == '__main__':
    main()
