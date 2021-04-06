from collections.abc import Iterable
from .vars import ColorPalette
import numpy as np
from powerlaw import plot_ccdf


def aaai_init_plot(plt, profile='1x2'):
    rc = {'axes.titlesize': 18, 'axes.labelsize': 16, 'legend.fontsize': 16,
          'font.size': 16, 'xtick.labelsize': 16, 'ytick.labelsize': 16}
    plt.rcParams.update(rc)
    if profile == '1x1':
        fig, ax = plt.subplots(1, 1, figsize=(10, 3.3))
        return ax
    elif profile == '1x2':
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))
        axes = axes.ravel()
        return axes
    elif profile == '1x3':
        fig, axes = plt.subplots(1, 3, figsize=(10, 3.3))
        axes = axes.ravel()
        return axes
    elif profile == '2x2':
        fig, axes = plt.subplots(2, 2, figsize=(10, 6.6))
        axes = axes.ravel()
        return axes


def concise_fmt(x, pos):
    if abs(x) // 1000000000 > 0:
        return '{0:.0f}B'.format(x / 1000000000)
    elif abs(x) // 1000000 > 0:
        return '{0:.0f}M'.format(x / 1000000)
    elif abs(x) // 1000 > 0:
        return '{0:.0f}K'.format(x / 1000)
    elif x == 10:
        return '10'
    elif x == 1:
        return '1'
    else:
        return '{0:.0f}'.format(x)


def exponent_fmt(x, pos):
    if x == 0:
        return '0'
    elif x == 1:
        return '1'
    elif x == 10:
        return '10'
    else:
        return '$10^{{{0}}}$'.format(int(np.log10(x)))


def exponent_fmt2(x, pos):
    if x == 0:
        return '1'
    elif x == 1:
        return '10'
    else:
        return '$10^{{{0}}}$'.format(int(x))


def exponent_fmt3(x, pos):
    if x < 0:
        return '0'
    elif x == 0:
        return '1'
    elif x == 1:
        return '10'
    else:
        return '$10^{{{0}}}$'.format(int(x))


def hide_spines(axes):
    if isinstance(axes, Iterable):
        for ax in axes:
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
    else:
        axes.spines['right'].set_visible(False)
        axes.spines['top'].set_visible(False)


def gini(arr):
    count = arr.size
    coefficient = 2 / count
    indexes = np.arange(1, count + 1)
    weighted_sum = (indexes * arr).sum()
    total = arr.sum()
    constant = (count + 1) / count
    return coefficient * weighted_sum / total - constant


def lorenz(arr):
    # this divides the prefix sum by the total sum
    # this ensures all the values are between 0 and 1.0
    scaled_prefix_sum = arr.cumsum() / arr.sum()
    # this prepends the 0 value (because 0% of all people have 0% of all wealth)
    return np.insert(scaled_prefix_sum, 0, 0)


def plot_dist_lorenz(axes, num_comment_list, color, ls, label, annotated=False):
    plot_ccdf(num_comment_list, ax=axes[0], color=color, ls=ls, label=label)
    sorted_comment_list = np.sort(np.array(num_comment_list))
    lorenz_curve = lorenz(sorted_comment_list)
    gini_coef = gini(sorted_comment_list)
    print('>>> In {0} videos,  Gini coefficient is {1:.4f}'.format(label, gini_coef))
    axes[1].plot(np.linspace(0.0, 1.0, lorenz_curve.size), lorenz_curve, color=color, ls=ls, label=label)
    if annotated:
        pinned_idx = next(x for x, val in enumerate(lorenz_curve) if val > 0.25)
        pinned_x = np.linspace(0.0, 1.0, lorenz_curve.size)[pinned_idx]
        pinned_y = 0.25
        axes[1].scatter([pinned_x], [pinned_y], c='r', s=30, marker='o', fc='r', ec='r', zorder=30)
        axes[1].text(pinned_x, pinned_y, '({0:.2f}%, {1:.0f}%)'.format(100 - 100 * pinned_x, 100 - pinned_y * 100),
                     size=14, horizontalalignment='right', verticalalignment='bottom')
