# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" Plot PDFs of (a) comments per video; (b) CCDF of comments per user.

Usage: python plot_fig3_data_profiling.py
Input data files: data/video_meta.csv, data/user_comment_meta.csv.bz2
Output image file: images/fig3_profiling.pdf
Time: ~1M
"""

import up  # go to root folder

import bz2, platform
import numpy as np
from scipy.signal import savgol_filter

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from powerlaw import plot_ccdf

from utils.helper import Timer
from utils.plot_conf import ColorPalette, aaai_init_plot, hide_spines, exponent_fmt, exponent_fmt3


def main():
    timer = Timer()
    timer.start()

    num_left_video_comment_list = []
    num_right_video_comment_list = []
    with open('data/video_meta.csv', 'r') as fin:
        fin.readline()
        for line in fin:
            _, _, video_leaning, _, _, num_comment_on_video, _ = line.rstrip().split(',', 6)
            num_comment_on_video = int(num_comment_on_video)
            if video_leaning == 'L':
                num_left_video_comment_list.append(num_comment_on_video)
            elif video_leaning == 'R':
                num_right_video_comment_list.append(num_comment_on_video)

    num_user_comment_list = []
    with bz2.BZ2File('data/user_comment_meta.csv.bz2', mode='r') as fin:
        fin.readline()
        for line in fin:
            line = line.decode('utf-8')
            num_comment_from_user = int(line.rstrip().split(',')[2])
            num_user_comment_list.append(num_comment_from_user)

    num_zero_comment_left_video = len([x for x in num_left_video_comment_list if x == 0])
    pct_zero_comment_left_video = 100 * len([x for x in num_left_video_comment_list if x == 0]) / len(num_left_video_comment_list)
    print('{0:,} ({1:.2f}%) left videos have 0 comment'.format(num_zero_comment_left_video, pct_zero_comment_left_video))
    num_left_video_comment_list = [np.log10(x) if x > 0 else -0.3 for x in num_left_video_comment_list]

    num_zero_comment_right_video = len([x for x in num_right_video_comment_list if x == 0])
    pct_zero_comment_right_video = 100 * len([x for x in num_right_video_comment_list if x == 0]) / len(num_right_video_comment_list)
    print('{0:,} ({1:.2f}%) right videos have 0 comment'.format(num_zero_comment_right_video, pct_zero_comment_right_video))
    num_right_video_comment_list = [np.log10(x) if x > 0 else -0.3 for x in num_right_video_comment_list]

    axes = aaai_init_plot(plt, profile='1x2')

    left_y2, left_x2 = np.histogram(num_left_video_comment_list, bins=50, density=True)
    new_left_x2 = [x for x, y in zip(left_x2[:-1], left_y2) if y != 0]
    new_left_y2 = [y for x, y in zip(left_x2[:-1], left_y2) if y != 0]
    new_left_y2 = savgol_filter(new_left_y2, window_length=9, polyorder=5)
    axes[0].fill_between(new_left_x2, new_left_y2, fc=(61/255, 133/255, 198/255, 0.25), ec=ColorPalette.LEFT_COLOR,
                         lw=1, label='Left video')

    right_y2, right_x2 = np.histogram(num_right_video_comment_list, bins=50, density=True)
    new_right_x2 = [x for x, y in zip(right_x2[:-1], right_y2) if y != 0]
    new_right_y2 = [y for x, y in zip(right_x2[:-1], right_y2) if y != 0]
    new_right_y2 = savgol_filter(new_right_y2, window_length=9, polyorder=5)
    axes[0].fill_between(new_right_x2, new_right_y2, fc=(204/255, 0, 0, 0.25), ec=ColorPalette.RIGHT_COLOR,
                         lw=1, label='Right video')

    axes[0].set_xlabel('#comments per video')
    axes[0].set_ylabel('density')
    axes[0].set_xticks([-0.3, 0, 1, 2, 3, 4, 5])
    axes[0].xaxis.set_major_formatter(FuncFormatter(exponent_fmt3))
    axes[0].set_xlim(xmin=-0.3)
    axes[0].set_ylim(ymin=0)
    axes[0].legend(loc='upper right', frameon=False, edgecolor='k', handlelength=1, handleheight=1)
    axes[0].set_title('(a)', pad=-2.9*72, y=1.0001)

    plot_ccdf(num_user_comment_list, ax=axes[1], color='k', ls='-', label='Total')
    pinned_x = 10
    pinned_y0 = len([x for x in num_user_comment_list if x >= pinned_x])
    pinned_y1 = len([x for x in num_user_comment_list if x >= pinned_x]) / len(num_user_comment_list)
    pinned_y2 = sum([x for x in num_user_comment_list if x >= pinned_x])
    pinned_y3 = sum([x for x in num_user_comment_list if x >= pinned_x]) / sum(num_user_comment_list)
    axes[1].scatter([pinned_x], [pinned_y1], s=40, marker='o', fc='w', ec='k', zorder=30)
    axes[1].text(pinned_x, pinned_y1, '({0}, {1:.1f}%)'.format(pinned_x, pinned_y1 * 100, pinned_y3 * 100),
                 horizontalalignment='left', verticalalignment='bottom')
    print('{0:,} ({1:.2f}%) users have at least {2} comments, they make up of {3:,} ({4:.2f}%) comments'
          .format(pinned_y0, pinned_y1 * 100, pinned_x, pinned_y2, pinned_y3 * 100))
    axes[1].set_xscale('log')
    axes[1].set_yscale('log')
    axes[1].set_xlabel('#comments per user')
    axes[1].set_xticks([1, 10, 100, 1000, 10000])
    axes[1].set_yticks([1, 0.001, 0.000001])
    axes[1].xaxis.set_major_formatter(FuncFormatter(exponent_fmt))
    axes[1].yaxis.set_major_formatter(FuncFormatter(exponent_fmt))
    axes[1].set_ylabel('$P(X \geq x)$')
    axes[1].set_title('(b)', pad=-2.9*72, y=1.0001)

    hide_spines(axes)

    timer.stop()

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig('images/fig3_profiling.pdf', bbox_inches='tight')
    if not platform.system() == 'Linux':
        plt.show()


if __name__ == '__main__':
    main()
