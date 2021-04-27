# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" Plot HAN classification results for 162K seed users.

Usage: python plot_fig4_han_accuracy.py
Input data files: hnatt/saved_models/hashed_cv[12345]_hnatt_prediction.json
Output image file: images/fig4_prediction_han.pdf
Time: ~1M
"""

import up  # go to root folder

import json, platform, bz2
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from utils.helper import Timer
from utils.plot_conf import ColorPalette, aaai_init_plot, hide_spines, concise_fmt


def convert_fmt(x, pos):
    return '{0:.1f}'.format(x / 20)


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def main():
    timer = Timer()
    timer.start()

    user_id_list = []
    y_true = []
    y_pred = []

    num_bin = 20
    num_cv = 5
    x_axis = range(num_bin)
    liberal_y_axis = [0] * len(x_axis)
    conservative_y_axis = [0] * len(x_axis)
    num_correct = 0

    hashed_user_id_dict = {}
    with bz2.BZ2File('data/hashed_user_ids.csv.bz2', 'r') as fin:
        fin.readline()
        for line in fin:
            line = line.decode('utf-8')
            user_id, hashed_user_id = line.rstrip().split(',')
            hashed_user_id_dict[user_id] = hashed_user_id

    for idx_fold in range(1, num_cv + 1):
        with open('hnatt/saved_models/hashed_cv{0}_hnatt_prediction.json'.format(idx_fold), 'w') as fout:
            with open('hnatt/saved_models/cv{0}_hnatt_prediction.json'.format(idx_fold), 'r') as fin:
                for line in fin:
                    record_json = json.loads(line.rstrip())
                    user_id = record_json['user_id']
                    if user_id in hashed_user_id_dict:
                        hashed_user_id = hashed_user_id_dict[user_id]
                        label = record_json['true']
                        pred_l = record_json['pred_l']
                        pred_r = record_json['pred_r']

                        fout.write('{0}\n'.format(json.dumps({'hashed_user_id': hashed_user_id,
                                                              'label': label,
                                                              'pred_l': pred_l,
                                                              'pred_r': pred_r,
                                                              })))

                        user_id_list.append(user_id)
                        pred_l = float(pred_l)
                        pred_r = float(pred_r)
                        y_pred.append(pred_r)
                        idx = min(num_bin - 1, int(pred_r * num_bin))
                        if label == 0:
                            y_true.append(0)
                            liberal_y_axis[idx] += 1
                            if pred_l > pred_r:
                                num_correct += 1
                        else:
                            y_true.append(1)
                            conservative_y_axis[idx] += 1
                            if pred_l < pred_r:
                                num_correct += 1

    for i in range(30):
        print(i, y_true[i], y_pred[i], user_id_list[i])
    print('accuracy {0}/{1}={2:.2f}%'.format(num_correct, len(y_true), 100*num_correct / len(y_true)))

    axes = aaai_init_plot(plt, profile='1x2')
    ax1, ax2 = axes

    ax1.bar(x_axis, conservative_y_axis, width=0.9, align='edge',
            color=(204/255, 0, 0, 0.25), edgecolor=ColorPalette.RIGHT_COLOR, lw=1)
    ax1.bar(x_axis, liberal_y_axis, width=0.9, align='edge',
            color=(61/255, 133/255, 198/255, 0.25), edgecolor=ColorPalette.LEFT_COLOR, lw=1, bottom=conservative_y_axis)
    ax1.set_xlabel('$P_r$')
    ax1.yaxis.set_major_formatter(FuncFormatter(concise_fmt))
    ax1.set_ylabel('frequency')

    twin_x = [x + 0.5 for x in x_axis]
    twin_y = [x / (x + y) if t >= num_bin / 2 else y / (x + y) for t, x, y in zip(x_axis, conservative_y_axis, liberal_y_axis)]

    ax2.plot(twin_x[:10], twin_y[:10], '-', color=ColorPalette.LEFT_COLOR)
    ax2.plot(twin_x[10:], twin_y[10:], '-', color=ColorPalette.RIGHT_COLOR)
    ax2.scatter(twin_x[0], twin_y[0], marker='o', s=30, c=ColorPalette.LEFT_COLOR)
    ax2.scatter(twin_x[19], twin_y[19], marker='o', s=30, c=ColorPalette.RIGHT_COLOR)
    ax2.scatter(twin_x[1:10], twin_y[1:10], marker='x', s=30, c=ColorPalette.LEFT_COLOR)
    ax2.scatter(twin_x[10:19], twin_y[10:19], marker='x', s=30, c=ColorPalette.RIGHT_COLOR)

    ax2.annotate('', xy=(1, 0.943), xycoords='data', xytext=(5, 0.943), textcoords='data',
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3', color=ColorPalette.LEFT_COLOR))
    ax2.text(2, 0.944, 'liberal', color=ColorPalette.LEFT_COLOR, ha='left', va='bottom', size=16)
    ax2.annotate('', xy=(19, 0.969), xycoords='data', xytext=(15, 0.969), textcoords='data',
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3', color=ColorPalette.RIGHT_COLOR))
    ax2.text(18, 0.97, 'conservative', color=ColorPalette.RIGHT_COLOR, ha='right', va='bottom', size=16)

    ax2.plot([1.5, 1.5], [0.82, 0.9], '--', lw=1, color='k')
    ax2.plot([18.5, 18.5], [0.82, 0.9], '--', lw=1, color='k')
    ax2.annotate('', xy=(1.5, 0.86), xycoords='data', xytext=(6.8, 0.86), textcoords='data',
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3', color='k', ls='dashed'))
    ax2.annotate('', xy=(13.2, 0.86), xycoords='data', xytext=(18.5, 0.86), textcoords='data',
                 arrowprops=dict(arrowstyle='<-', connectionstyle='arc3', color='k', ls='dashed'))
    ax2.text(10, 0.86, 'unknown', color='k', ha='center', va='center', size=16)

    ax2.set_xlabel('$P_r$: how likely to be conservative?')
    ax2.set_ylabel('accuracy')
    ax2.set_ylim(0.38, 1.02)
    ax2.tick_params(axis='y', which='major', labelsize=16)

    for ax in axes:
        ax.set_xlim(-1, 21)
        ax.set_xticks([0, 10, 20])
        ax.xaxis.set_major_formatter(FuncFormatter(convert_fmt))

    axes[0].set_title('(a)', pad=-2.9*72, y=1.0001)
    axes[1].set_title('(b)', pad=-2.9*72, y=1.0001)

    hide_spines(axes)

    timer.stop()

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig('../images/fig4_prediction_han.pdf', bbox_inches='tight')
    if not platform.system() == 'Linux':
        plt.show()


if __name__ == '__main__':
    main()
