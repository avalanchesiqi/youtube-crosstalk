# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" How many cross-partisan comments do videos attract?

Usage: python plot_fig7_prevalence_on_video.py
Input data files: ../data/video_meta.csv
Output image file: ../images/fig7_video_comment_dist.pdf
Time: ~1M
"""

import up  # go to root folder

import platform
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

    even_split_points = list(np.linspace(3, 6, 21))
    thresholds = [10 ** x for x in even_split_points]
    len_threshold = len(thresholds)

    bin_stats = defaultdict(int)
    left_comment_dist = [[] for _ in range(len_threshold)]
    right_comment_dist = [[] for _ in range(len_threshold)]

    all_left = []
    all_right = []

    with open('data/video_meta.csv', 'r') as fin:
        fin.readline()
        for line in fin:
            _, _, video_leaning, _, num_view, num_comment, \
                num_comment_from_left, num_comment_from_right, _ = line.rstrip().split(',', 8)
            num_view = int(num_view)
            num_comment = int(num_comment)
            num_comment_from_left = int(num_comment_from_left)
            num_comment_from_right = int(num_comment_from_right)

            if num_comment >= 10:
                bin_idx = find_bin_idx(num_view, thresholds)
                bin_stats[bin_idx] += 1
                if video_leaning == 'L':
                    left_comment_dist[bin_idx].append(num_comment_from_right / num_comment * 100)
                    all_left.append(num_comment_from_right / num_comment)
                elif video_leaning == 'R':
                    right_comment_dist[bin_idx].append(num_comment_from_left / num_comment * 100)
                    all_right.append(num_comment_from_left / num_comment)

    left_y_axis = []
    right_y_axis = []
    left_25_y_axis = []
    right_25_y_axis = []
    left_75_y_axis = []
    right_75_y_axis = []

    for bin_idx in range(len_threshold):
        print('{0} videos in bin {1}, threshold {2}'.format(bin_stats[bin_idx], bin_idx + 1, thresholds[bin_idx]))
        print('left videos', len(left_comment_dist[bin_idx]), np.mean(left_comment_dist[bin_idx]), np.std(left_comment_dist[bin_idx]))
        print('right videos', len(right_comment_dist[bin_idx]), np.mean(right_comment_dist[bin_idx]), np.std(right_comment_dist[bin_idx]))
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
    axes[0].set_xlabel('#views on a video')
    axes[0].set_ylabel('%comments\nfrom conservatives')

    axes[1].plot(thresholds, right_y_axis, '-o', c=ColorPalette.LEFT_COLOR, ms=6)
    axes[1].plot(thresholds, right_25_y_axis, '--', c=ColorPalette.LEFT_COLOR)
    axes[1].plot(thresholds, right_75_y_axis, '--', c=ColorPalette.LEFT_COLOR)
    axes[1].set_xlabel('#views on a video')
    axes[1].set_ylabel('%comments\nfrom liberals')

    for ax in axes:
        ax.set_yticks([0, 30, 60])
        ax.set_ylim([-1.5, 66])
        ax.set_xscale('log')
        ax.set_xticks([1000, 10000, 100000, 1000000])
        ax.minorticks_off()

    axes[0].set_title('(a) left-leaning', pad=-2.9 * 72, y=1.0001)
    axes[1].set_title('(b) right-leaning', pad=-2.9 * 72, y=1.0001)

    hide_spines(axes)

    timer.stop()

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig('images/fig7_video_comment_dist.pdf', bbox_inches='tight')
    if not platform.system() == 'Linux':
        plt.show()


if __name__ == '__main__':
    main()
