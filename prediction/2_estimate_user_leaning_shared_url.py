# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" Estimate user political leanings based on shared videos in user comments.

Usage: python 2_estimate_user_leaning_shared_url.py
Input data files: data/us_partisan.csv,
                  prediction/data/comment_url_list.tsv.bz2
Output data file: prediction/2_url_seed_user_label_{threshold}.csv
Time: ~10S
"""

import up  # go to root folder

import bz2
from tldextract import extract

from utils.helper import bias_metric, Timer


def main():
    timer = Timer()
    timer.start()

    domain_leaning_dict = {}
    with open('data/us_partisan.csv', 'r') as fin:
        # title, url, channel_title, channel_id, leaning, type, source, channel_description
        fin.readline()
        for line in fin:
            _, url, _, _, leaning, _ = line.rstrip().split(',', 5)
            parsed_url = extract(url)
            domain_url = '{0}.{1}'.format(parsed_url.domain, parsed_url.suffix).upper()
            if domain_url not in domain_leaning_dict:
                domain_leaning_dict[domain_url] = leaning

    print('we have leanings for {0} domains'.format(len(domain_leaning_dict)))

    predicted_left_cnt = 0
    predicted_right_cnt = 0
    conflict_cnt = 0
    threshold = 5
    with open('prediction/2_url_seed_user_label_{0}.csv'.format(threshold), 'w') as fout:
        with bz2.BZ2File('prediction/data/comment_url_list.tsv.bz2', 'r') as fin:
            for line in fin:
                line = line.decode('utf-8')
                user_id, domain_stats = line.rstrip().split('\t', 1)
                domain_freq_list = domain_stats.split()
                domain_freq_dict = {x.split(',')[0]: int(x.split(',')[-1]) for x in domain_freq_list}

                num_left_domain = 0
                num_right_domain = 0
                if 'LEFT_VIDEO' in domain_freq_dict:
                    num_left_domain += domain_freq_dict['LEFT_VIDEO']
                if 'RIGHT_VIDEO' in domain_freq_dict:
                    num_right_domain += domain_freq_dict['RIGHT_VIDEO']
                for domain, freq in domain_freq_dict.items():
                    if domain in domain_leaning_dict:
                        if domain_leaning_dict[domain] == 'L':
                            num_left_domain += freq
                        elif domain_leaning_dict[domain] == 'R':
                            num_right_domain += freq

                if (num_left_domain + num_right_domain) >= threshold:
                    bipartisan_bias = bias_metric(num_left_domain, num_right_domain)
                    if bipartisan_bias <= -0.9:
                        predicted_left_cnt += 1
                        fout.write('{0},{1}\n'.format(user_id, 'L'))
                    elif bipartisan_bias >= 0.9:
                        predicted_right_cnt += 1
                        fout.write('{0},{1}\n'.format(user_id, 'R'))
                    else:
                        conflict_cnt += 1
                        # print('{0},{1},{2}'.format(user_id, num_left_domain, num_right_domain))
                        # print('=' * 79)

    print('>>> predicted {0} left users'.format(predicted_left_cnt))
    print('>>> predicted {0} right users'.format(predicted_right_cnt))
    print('>>> in total, predicted {0} users'.format(predicted_left_cnt + predicted_right_cnt))
    print('>>> {0} conflicted user by url'.format(conflict_cnt))

    timer.stop()


if __name__ == '__main__':
    main()
