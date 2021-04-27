# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" Which media types attract more cross-partisan comments?

Usage: python plot_fig8_cp_by_media_type.py
Input data files: data/video_meta.csv
Output image file: images/fig8_cp_by_media_type.pdf
Time: ~1M
"""

import up  # go to root folder

import platform
import numpy as np
from collections import defaultdict
import pandas as pd
import pingouin as pg

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style(style='white')

from utils.helper import Timer
from utils.plot_conf import hide_spines, aaai_init_plot


def main():
    timer = Timer()
    timer.start()

    left_channel_cp_dict = defaultdict(list)
    right_channel_cp_dict = defaultdict(list)

    cid_type_dict = {}
    with open('data/video_meta.csv', 'r') as fin:
        fin.readline()
        for line in fin:
            _, channel_id, media_leaning, media_type, _, num_comment, \
                num_cmt_from_liberal, num_cmt_from_conservative, _ = line.rstrip().split(',', 8)
            num_comment = int(num_comment)
            num_cmt_from_liberal = int(num_cmt_from_liberal)
            num_cmt_from_conservative = int(num_cmt_from_conservative)
            if num_comment >= 10:
                cid_type_dict[channel_id] = media_type
                if media_leaning == 'L':
                    left_channel_cp_dict[channel_id].append(num_cmt_from_conservative / num_comment * 100)
                elif media_leaning == 'R':
                    right_channel_cp_dict[channel_id].append(num_cmt_from_liberal / num_comment * 100)

    example_left_channels = {'UCupvZG-5ko_eiXAupbDfxWw': -2,  # CNN
                             'UCaXkIU1QidjPwiAYu6GcHjg': -3,  # MSNBC
                             'UCBi2mrWuNuyYy4gbM6fU18Q': -4,  # ABC News
                             }
    for channel_id in example_left_channels:
        print(channel_id, cid_type_dict[channel_id],
              np.mean(left_channel_cp_dict[channel_id]), np.std(left_channel_cp_dict[channel_id]))
    print('-' * 79)

    example_right_channels = {'UCXIJgqnII2ZOINSWNOGFThA': 2,  # Fox News
                              'UCe02lGcO-ahAURWuxAJnjdA': 3,  # Timcast
                              'UCLoNQH9RCndfUGOb2f7E1Ew': 4,  # The Next News Network
                              }
    for channel_id in example_right_channels:
        print(channel_id, cid_type_dict[channel_id],
              np.mean(right_channel_cp_dict[channel_id]), np.std(right_channel_cp_dict[channel_id]))
    print('-' * 79)

    topic_list = []
    party_list = []
    cp_list = []

    left_list = [0] * 4
    right_list = [0] * 4

    for channel_id, v in left_channel_cp_dict.items():
        if len(v) >= 5:
            party_list.append('Left')
            cp_list.append(np.mean(left_channel_cp_dict[channel_id]))
            if cid_type_dict[channel_id] == 'national':
                topic_list.append('national')
                left_list[0] += 1
            elif cid_type_dict[channel_id] == 'local':
                topic_list.append('local')
                left_list[1] += 1
            elif cid_type_dict[channel_id] == 'organization':
                topic_list.append('organization')
                left_list[2] += 1
            elif cid_type_dict[channel_id] == 'independent':
                topic_list.append('independent')
                left_list[3] += 1

    for channel_id, v in right_channel_cp_dict.items():
        if len(v) >= 5:
            party_list.append('Right')
            cp_list.append(np.mean(right_channel_cp_dict[channel_id]))
            if cid_type_dict[channel_id] == 'national':
                topic_list.append('national')
                right_list[0] += 1
            elif cid_type_dict[channel_id] == 'local':
                topic_list.append('local')
                right_list[1] += 1
            elif cid_type_dict[channel_id] == 'organization':
                topic_list.append('organization')
                right_list[2] += 1
            elif cid_type_dict[channel_id] == 'independent':
                topic_list.append('independent')
                right_list[3] += 1

    print()
    print('num of left-leaning national, local, organization, independent media', left_list)
    print('num of right-leaning national, local, organization, independent media', right_list)
    print('total number of media that have at least 5 videos with at least 10 comments', sum(left_list) + sum(right_list))
    print()

    df = pd.DataFrame({'topic': topic_list, 'party': party_list, 'cp_list': cp_list})

    for topic in ['national', 'local', 'organization', 'independent']:
        for metric in ['cp_list']:
            left = df[(df.topic == topic) & (df.party == 'Left')][metric]
            right = df[(df.topic == topic) & (df.party == 'Right')][metric]
            print(topic, metric)
            print(np.median(left), np.median(right))
            print(pg.mwu(left, right, tail='one-sided'))
            print('-' * 79)

    ax1 = aaai_init_plot(plt, profile='1x1')
    sns.violinplot(x=df["topic"], y=df['cp_list'], hue=df["party"],
                   palette={"Right": "#e06666", "Left": "#6d9eeb"},
                   inner="quartile",
                   linewidth=1.5, cut=1.5,
                   ax=ax1, order=["national", "local", "organization", "independent"],
                   scale="area", split=True, width=0.7, hue_order=['Left', 'Right'])

    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles=handles[0:], labels=['left channel', 'right channel'], loc='upper left', frameon=False, edgecolor='k', handlelength=1, handleheight=1)
    ax1.set(xlabel=None)
    ax1.set_yticks([0, 50, 100])
    ax1.set_ylabel('%cross-talk')
    ax1.set_ylim([-10, 102])

    hide_spines(ax1)

    timer.stop()

    plt.tight_layout()
    plt.savefig('images/fig8_cp_by_media_type.pdf', bbox_inches='tight')
    if not platform.system() == 'Linux':
        plt.show()


if __name__ == '__main__':
    main()
