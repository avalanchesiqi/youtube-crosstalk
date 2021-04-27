#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Given a channel username, getting YouTube channel id or validate the id.

Usage: python 6_get_channel_id.py
Input data files: data/mbfc/mbfc_ratings_v5.csv
Output data files: data/mbfc/mbfc_ratings_v6.csv
Time: 5M for MBFC
"""

import up  # go to root folder

import conf.local_conf as conf
from utils.helper import Timer
from utils.crawlers import YTCrawler


def main():
    timer = Timer()
    timer.start()

    youtube_key = conf.youtube_key
    parts = 'id'

    yt_crawler = YTCrawler()
    yt_crawler.set_key(youtube_key)

    app_name = 'mbfc'

    with open('data/{0}/{0}_ratings_v6.csv'.format(app_name), 'w') as fout:
        with open('data/{0}/{0}_ratings_v5.csv'.format(app_name), 'r') as fin:
            fout.write(fin.readline())
            for line in fin:
                title, tail = line.rstrip().split(',', 1)
                middle, yt_id, yt_user = tail.rsplit(',', 2)
                if yt_id == '' and yt_user == '':
                    fout.write(line)
                elif yt_id != '':
                    yt_id = yt_crawler.check_channel_id(yt_id, parts)
                    if yt_id == '':
                        print('--- Channel id crawler failed on title {0}'.format(title))
                    fout.write('{0},{1},{2},{3}\n'.format(title, middle, yt_id, yt_user))
                else:
                    yt_id = yt_crawler.get_channel_id(yt_user, parts)
                    if yt_id == '':
                        print('--- Channel id crawler failed on title {0}'.format(title))
                    fout.write('{0},{1},{2},{3}\n'.format(title, middle, yt_id, yt_user))

    timer.stop()


if __name__ == '__main__':
    main()
