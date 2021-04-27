#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Searching for the unresolved Twitter accounts by querying Twitter search API with media titles.

Usage: python 4_search_twitter_handle.py
Input data files: data/mbfc/mbfc_ratings_v3.csv
Output data files: data/mbfc/mbfc_ratings_v4.csv
Time: 40M for MBFC
"""

import up  # go to root folder

import tldextract
from difflib import SequenceMatcher
from tweepy import OAuthHandler, API

import conf.local_conf as conf
from utils.helper import Timer
from utils.crawlers import get_domain, match_website_on_twitter_page


def main():
    timer = Timer()
    timer.start()

    consumer_key = conf.twitter_consumer_key
    consumer_secret = conf.twitter_consumer_secret
    access_token = conf.twitter_access_token
    access_token_secret = conf.twitter_access_secret

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)

    app_name = 'mbfc'

    num_hit_twitter = 0
    num_fail_twitter = 0
    num_request = 0

    # searching Twitter Search API for tweet handles if we cannot find it on webpage
    with open('data/{0}/{0}_ratings_v4.csv'.format(app_name), 'w') as fout:
        with open('data/{0}/{0}_ratings_v3.csv'.format(app_name), 'r') as fin:
            fout.write(fin.readline())
            for line in fin:
                title, tail = line.rstrip().split(',', 1)
                middle, website_url, tw_handle, tw_sim, yt_id, yt_user = tail.rsplit(',', 5)
                if tw_handle == '':
                    print('===============')
                    print('media title', title)
                    print('website url', website_url)
                    # get the first 10 Twitter users
                    returned_users = api.search_users(title, count=10)
                    num_request += 1
                    to_write = True
                    for user in returned_users:
                        user_json = user._json
                        screen_name = user_json['screen_name'].lower()
                        if match_website_on_twitter_page(user_json, website_url):
                            selected_tw_handle = screen_name
                            num_hit_twitter += 1
                            tw_similarity = SequenceMatcher(None, tldextract.extract(get_domain(website_url)).domain, selected_tw_handle).ratio()
                            fout.write('{0},{1},{2},{3},{4},{5},{6}\n'.format(title, middle, website_url, selected_tw_handle, tw_similarity, yt_id, yt_user))
                            to_write = False
                            print('find twitter handle:', selected_tw_handle)
                            print('success index {0}/{2}: {1}'.format(num_hit_twitter, title, num_request))
                            break
                    if to_write:
                        num_fail_twitter += 1
                        fout.write(line)
                        print('xxx failed to find for this media {0}, {1}!'.format(title, website_url))
                        print('fail index {0}/{2}: {1}'.format(num_fail_twitter, title, num_request))
                else:
                    fout.write(line)

    print('number of requests sent: {0}'.format(num_request))
    timer.stop()


if __name__ == '__main__':
    main()
