# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" Bias in YouTube’s Comment Sorting.

Usage: python plot_fig9_position_bias.py
Input data files: ../data/video_meta.csv
Output image file: ../images/fig9_position_bias.pdf
Time: ~4M
"""

import up  # go to root folder


import sys, os, platform, bz2, json, pickle
from collections import defaultdict
import numpy as np
import scipy.stats

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from utils.helper import Timer
from utils.plot_conf import ColorPalette, aaai_init_plot, hide_spines, exponent_fmt


def main():
    timer = Timer()
    timer.start()

    max_top_position = 20
    lib_on_right = [0] * max_top_position
    con_on_left = [0] * max_top_position
    num_selected_left_video = 0
    num_selected_right_video = 0

    left_benchmark = []
    right_benchmark = []
    with open('data/video_meta.csv', 'r') as fin:
        fin.readline()
        for line in fin:
            _, _, video_leaning, _, _, num_comment, num_cmt_from_liberal, num_cmt_from_conservative, _,\
                num_top_comment, top_leanings = line.rstrip().split(',')
            num_comment = int(num_comment)
            num_top_comment = int(num_top_comment)
            if num_comment > max_top_position and num_top_comment == max_top_position:
                num_cmt_from_liberal = int(num_cmt_from_liberal)
                num_cmt_from_conservative = int(num_cmt_from_conservative)

                if video_leaning == 'L':
                    num_selected_left_video += 1
                    left_benchmark.append(num_cmt_from_conservative/num_comment * 100)
                    for position_idx, top_leaning in enumerate(top_leanings):
                        if top_leaning == 'R':
                            con_on_left[position_idx] += 1
                elif video_leaning == 'R':
                    num_selected_right_video += 1
                    right_benchmark.append(num_cmt_from_liberal/num_comment * 100)
                    for position_idx, top_leaning in enumerate(top_leanings):
                        if top_leaning == 'L':
                            lib_on_right[position_idx] += 1

    fraction_con_on_left = [x / num_selected_left_video * 100 for x in con_on_left]
    fraction_lib_on_right = [x / num_selected_right_video * 100 for x in lib_on_right]

    print(np.mean(left_benchmark), num_selected_left_video)
    print(np.mean(right_benchmark), num_selected_right_video)

    axes = aaai_init_plot(plt, profile='1x2')

    print(fraction_con_on_left)
    print(fraction_lib_on_right)

    num_position = 20
    x_axis = range(1, num_position + 1)
    axes[0].plot(x_axis, fraction_con_on_left, color=ColorPalette.RIGHT_COLOR, ls='--', marker='o', ms=6)
    axes[0].set_ylabel('%comments\nfrom conservatives')
    axes[0].set_title('(a) left video', pad=-2.9*72, y=1.0001)
    axes[0].bar(num_position + 4, np.mean(left_benchmark), align='center', width=2,
                color=(204 / 255, 0, 0, 0.25),
                edgecolor=ColorPalette.RIGHT_COLOR,
                ecolor='k', capsize=10)
    axes[0].bar(num_position + 4, np.mean(left_benchmark), align='center', width=2,
                color='None',
                edgecolor=ColorPalette.RIGHT_COLOR, hatch='//')
    axes[0].text(num_position + 4, np.mean(left_benchmark) + 1, '{0:.1f}'.format(np.mean(left_benchmark)), va='bottom', ha='center')

    axes[1].plot(x_axis, fraction_lib_on_right,
                 color=ColorPalette.LEFT_COLOR, ls='--', marker='o', ms=6)
    axes[1].set_ylabel('%comments\nfrom liberals')
    axes[1].set_title('(b) right video', pad=-2.9*72, y=1.0001)
    axes[1].bar(num_position + 4, np.mean(right_benchmark), align='center', width=2,
                color=(61/255, 133/255, 198/255, 0.25),
                edgecolor=ColorPalette.LEFT_COLOR,
                ecolor='k', capsize=10)
    axes[1].bar(num_position + 4, np.mean(right_benchmark), align='center', width=2,
                color='None',
                edgecolor=ColorPalette.LEFT_COLOR, hatch='//')
    axes[1].text(num_position + 4, np.mean(right_benchmark) + 1, '{0:.1f}'.format(np.mean(right_benchmark)), va='bottom', ha='center')

    for ax in axes:
        ax.set_ylim([0, 33])
        ax.set_xticks([1, 5, 10, 15, 20, 24])
        ax.set_xticklabels([1, 5, 10, 15, 20, 'all'])
        ax.set_xlabel('top comment position')

    hide_spines(axes)

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig('images/fig9_position_bias.pdf', bbox_inches='tight')
    if not platform.system() == 'Linux':
        plt.show()

    timer.stop()


if __name__ == '__main__':
    main()
