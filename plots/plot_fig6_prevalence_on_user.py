# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" How often do users post on opposing channels?

Usage: python plot_fig6_prevalence_on_user.py
Input data files: data/user_comment_meta.csv.bz2
Output image file: images/fig6_user_comment_dist.pdf
Time: ~1M
"""

import up  # go to root folder

import platform, bz2
import numpy as np
from collections import defaultdict

import matplotlib.pyplot as plt

from utils.helper import Timer
from utils.plot_conf import hide_spines, aaai_init_plot, ColorPalette


def find_bin_idx(num_comment, thresholds):
    ret = 0
    for idx in range(len(thresholds)):
        if thresholds[idx] <= num_comment:
            ret = idx
        if idx == len(thresholds) - 1 or num_comment < thresholds[idx + 1]:
            break
    return ret


def main():
    timer = Timer()
    timer.start()

    even_split_points = list(np.linspace(1, 3.5, 21))
    thresholds = [10**x for x in even_split_points]
    len_threshold = len(thresholds)

    left_comment_dist = [[] for _ in range(len_threshold)]
    right_comment_dist = [[] for _ in range(len_threshold)]

    total_left_comment = 0
    total_right_comment = 0
    bin_stats = defaultdict(int)
    num_left = 0
    num_right = 0
    all_left = []
    all_right = []
    with bz2.BZ2File('data/user_comment_meta.csv.bz2', 'r') as fin:
        fin.readline()
        for line in fin:
            line = line.decode('utf-8')
            user_id, user_leaning, num_comment, num_comment_on_left, num_comment_on_right = line.rstrip().split(',')
            num_comment = int(num_comment)
            num_comment_on_left = int(num_comment_on_left)
            num_comment_on_right = int(num_comment_on_right)

            if num_comment >= 10 and user_leaning != 'U':
                bin_idx = find_bin_idx(num_comment, thresholds)
                bin_stats[bin_idx] += 1
                if user_leaning == 'L':
                    num_left += 1
                    total_left_comment += num_comment
                    left_comment_dist[bin_idx].append(num_comment_on_right / num_comment * 100)
                    all_left.append(num_comment_on_right / num_comment)
                elif user_leaning == 'R':
                    num_right += 1
                    total_right_comment += num_comment
                    right_comment_dist[bin_idx].append(num_comment_on_left / num_comment * 100)
                    all_right.append(num_comment_on_left / num_comment)

    print(num_left, num_right)
    print(np.mean(all_left), np.median(all_left))
    print(np.mean(all_right), np.median(all_right))
    print('left users post {0:,} comments, right users post {1:,} comments'.format(total_left_comment, total_right_comment))
    left_y_axis = []
    right_y_axis = []
    left_25_y_axis = []
    right_25_y_axis = []
    left_75_y_axis = []
    right_75_y_axis = []

    for bin_idx in range(len_threshold):
        print('{0} users in bin {1}, threshold {2}'.format(bin_stats[bin_idx], bin_idx + 1, thresholds[bin_idx]))
        print('left user', len(left_comment_dist[bin_idx]), np.mean(left_comment_dist[bin_idx]), np.std(left_comment_dist[bin_idx]))
        print('right user', len(right_comment_dist[bin_idx]), np.mean(right_comment_dist[bin_idx]), np.std(right_comment_dist[bin_idx]))
        left_y_axis.append(np.median(left_comment_dist[bin_idx]))
        right_y_axis.append(np.median(right_comment_dist[bin_idx]))
        left_25_y_axis.append(np.percentile(left_comment_dist[bin_idx], 25))
        right_25_y_axis.append(np.percentile(right_comment_dist[bin_idx], 25))
        left_75_y_axis.append(np.percentile(left_comment_dist[bin_idx], 75))
        right_75_y_axis.append(np.percentile(right_comment_dist[bin_idx], 75))

    axes = aaai_init_plot(plt, profile='1x2')

    axes[0].plot(thresholds, left_y_axis, '-o', c=ColorPalette.RIGHT_COLOR, ms=6)
    axes[0].plot(thresholds, left_25_y_axis, '--', c=ColorPalette.RIGHT_COLOR)
    axes[0].plot(thresholds, left_75_y_axis, '--', c=ColorPalette.RIGHT_COLOR)
    axes[0].set_xlabel('#comments by a user')
    axes[0].set_ylabel('%comments\non right videos')

    axes[1].plot(thresholds, right_y_axis, '-o', c=ColorPalette.LEFT_COLOR, ms=6)
    axes[1].plot(thresholds, right_25_y_axis, '--', c=ColorPalette.LEFT_COLOR)
    axes[1].plot(thresholds, right_75_y_axis, '--', c=ColorPalette.LEFT_COLOR)
    axes[1].set_xlabel('#comments by a user')
    axes[1].set_ylabel('%comments\non left videos')

    for ax in axes:
        ax.set_yticks([0, 40, 80])
        ax.set_ylim([-2, 85])
        ax.set_xscale('log')
        ax.set_xticks([10, 100, 1000])
        ax.minorticks_off()

    axes[0].set_title('(a) liberal', pad=-2.9 * 72, y=1.0001)
    axes[1].set_title('(b) conservative', pad=-2.9 * 72, y=1.0001)

    hide_spines(axes)

    timer.stop()

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig('images/fig6_user_comment_dist.pdf', bbox_inches='tight')
    if not platform.system() == 'Linux':
        plt.show()


if __name__ == '__main__':
    main()
