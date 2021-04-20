# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" The percentage of users who commented on both left-leaning and right-leaning channels,
varying by the number of comments they posted.

Usage: python plot_fig10_cp_by_user_comment.py
Input data files: ../data/user_comment_trace.csv.bz2
Output image file: ../images/fig10_cp_by_user_comment.pdf
Time: ~1M
"""

import up  # go to root folder

import platform, bz2

import matplotlib.pyplot as plt

from utils.helper import Timer
from utils.plot_conf import hide_spines, aaai_init_plot, ColorPalette


def main():
    timer = Timer()
    timer.start()

    thresholds = range(2, 31)
    num_user = [0] * len(thresholds)
    num_left_user = [0] * len(thresholds)
    num_right_user = [0] * len(thresholds)
    num_cross_user = [0] * len(thresholds)

    with bz2.BZ2File('data/user_comment_meta.csv.bz2', 'r') as fin:
        fin.readline()
        for line in fin:
            line = line.decode('utf-8')
            hashed_user_id, predicted_user_leaning, num_comment, num_cmt_on_left, num_cmt_on_right = line.rstrip().split(',')
            num_comment = int(num_comment)
            num_cmt_on_left = int(num_cmt_on_left)
            num_cmt_on_right = int(num_cmt_on_right)

            for idx, threshold in enumerate(thresholds):
                if num_comment >= threshold:
                    num_user[idx] += 1
                    if num_cmt_on_left == 0:
                        num_right_user[idx] += 1
                    elif num_cmt_on_right == 0:
                        num_left_user[idx] += 1
                    else:
                        num_cross_user[idx] += 1

    y_axis = []
    for idx, threshold in enumerate(thresholds):
        print(threshold, num_user[idx], num_left_user[idx], num_right_user[idx], num_cross_user[idx])
        print(num_cross_user[idx] / num_user[idx] * 100)
        y_axis.append(num_cross_user[idx] / num_user[idx] * 100)
        print()

    ax1 = aaai_init_plot(plt, profile='1x1')

    # ax1.plot(thresholds, y_axis, '-ko', mfc='none', )
    # marker_style = dict(color=ColorPalette.LEFT_COLOR, linestyle='none', marker='o',
    #                     markersize=12, markerfacecoloralt=ColorPalette.RIGHT_COLOR)
    # ax1.plot(thresholds, y_axis, fillstyle=Line2D.fillStyles[1], **marker_style)
    ax1.plot(thresholds, y_axis, 'ok', mfc='none', ms=8)

    ax1.set_xlabel('#comments posted by user')
    ax1.set_ylabel('%users who comment\non both partisans')

    ax1.set_yticks([40, 60, 80])
    ax1.set_ylim([35, 90])
    ax1.set_xticks([2, 5, 10, 15, 20, 25, 30])

    hide_spines(ax1)

    timer.stop()

    plt.tight_layout()
    plt.savefig('images/fig10_cp_by_user_comment.pdf', bbox_inches='tight')
    if not platform.system() == 'Linux':
        plt.show()


if __name__ == '__main__':
    main()
