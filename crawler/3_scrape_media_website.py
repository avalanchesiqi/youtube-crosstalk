# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" Scraping news media website for social media (Twitter + YouTube) accounts.
You need review the media with low similarity or redirected url, looking for log line starting with +++. For example,
+++ Twitter handle to be reviewed: petergrier 0.2105

Usage: python 3_scrape_media_website.py
Input data files: data/mbfc/mbfc_ratings_v2.csv
Output data files: data/mbfc/mbfc_ratings_v3.csv
Time: 2H for MBFC
"""

import up  # go to root folder

import time, requests, re, random, tldextract
from collections import defaultdict
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from tweepy import OAuthHandler, API

import conf.local_conf as conf
from utils.helper import Timer
from utils.crawlers import USER_AGENT_LIST, YOUTUBE_CHANNEL_ABOUT, YOUTUBE_USER_ABOUT
from utils.crawlers import get_domain, match_website_on_twitter_page, match_links_on_youtube_page


def crawl_social_media_from_url(website_url, api):
    print('===============')
    print('website url', website_url)
    domain = get_domain(website_url)
    tw_handles_cnt = defaultdict(int)
    yt_ids_cnt = defaultdict(int)
    yt_users_cnt = defaultdict(int)
    try:
        response = requests.get(website_url,
                                headers={'User-Agent': random.choice(USER_AGENT_LIST)},
                                allow_redirects=False)
    except:
        response = requests.get(website_url, allow_redirects=False)
    time.sleep(1)
    if response.text.strip() == '':
        try:
            response = requests.get(website_url,
                                    headers={random.choice(USER_AGENT_LIST)},
                                    allow_redirects=True)
        except:
            response = requests.get(website_url, allow_redirects=True)
        print('+++ Need review for URL {0}, redirected URL {1}'.format(website_url, response.url))
    soup = BeautifulSoup(response.text, 'lxml')
    website_links = soup.find_all('a', href=True)
    for website_link in website_links:
        website_link = website_link.get('href')
        website_link = re.sub(r'(https?://)?(www\d?.)?', '', website_link)
        website_link = website_link.replace('@', '').strip().strip('/')
        # twitter link
        lower_case_website_link = website_link.lower()
        if lower_case_website_link.startswith('twitter.com'):
            if bool(re.match(r'twitter.com/[\w]+\??|/?$', lower_case_website_link)) and \
                    not bool(re.match(r'twitter.com/(intent|share|home|hashtag)/?', lower_case_website_link)) and \
                    not bool(re.match(r'twitter.com/[\w]+/status?', lower_case_website_link)):
                tw_handle = re.split(r'/|\?', lower_case_website_link)[1]
                tw_handles_cnt[tw_handle] += 1
            #     print('find twitter handle:', tw_handle)
            # else:
            #     print('non-twitter handle url:', website_link)
        # youtube link
        elif lower_case_website_link.startswith('youtube.com'):
            # do NOT lower cases the channel id! channel id is case-sensitive
            if bool(re.match(r'youtube.com/channel/[\w]+/?', lower_case_website_link)):
                yt_id = re.split(r'/|\?', website_link)[2]
                yt_id = re.split('[^a-zA-Z0-9_-]', yt_id)[0]
                yt_ids_cnt[yt_id] += 1
                # print('find youtube id:', yt_id)
            else:
                if bool(re.match(r'youtube.com/user/[\w]+/?', lower_case_website_link)):
                    yt_user = re.split(r'/|\?', website_link)[2]
                    yt_user = re.split('\W', yt_user)[0]
                    yt_users_cnt[yt_user] += 1
                    # print('find youtube user:', yt_user)
                elif bool(re.match(r'youtube.com/[\w]+/?$', lower_case_website_link)):
                    yt_user = re.split(r'/', website_link)[1]
                    yt_user = re.split('\W', yt_user)[0]
                    yt_users_cnt[yt_user] += 1
                    # print('find youtube user:', yt_user)
                elif bool(re.match(r'youtube.com/[\w]+\?sub_confirmation=1', lower_case_website_link)):
                    yt_user = re.split(r'/|\?', website_link)[1]
                    yt_user = re.split('\W', yt_user)[0]
                    yt_users_cnt[yt_user] += 1
                #     print('find youtube user:', yt_user)
                # else:
                #     print('non-youtube channel url:', website_link)

    # selecting the matched tweet handle, the matched tweet handle should list the url on the user description page
    selected_tw_handle = ''
    tw_similarity = ''
    if len(tw_handles_cnt) > 1:
        tw_handles_list = sorted(list(tw_handles_cnt.keys()), key=lambda x: tw_handles_cnt[x], reverse=True)
        try:
            returned_users = api.lookup_users(screen_names=tw_handles_list)
            for user in returned_users:
                user_json = user._json
                screen_name = user_json['screen_name'].lower()
                if match_website_on_twitter_page(user_json, website_url):
                    selected_tw_handle = screen_name
                    break
        except Exception as e:
            # print(str(e))
            for tw_handle in tw_handles_list:
                try:
                    returned_user = api.lookup_users(screen_names=[tw_handle])[0]
                    user_json = returned_user._json
                    screen_name = user_json['screen_name'].lower()
                    if match_website_on_twitter_page(user_json, website_url):
                        selected_tw_handle = screen_name
                        break
                except:
                    pass
    elif len(tw_handles_cnt) == 1:
        selected_tw_handle = list(tw_handles_cnt.keys())[0]

    if selected_tw_handle != '':
        tw_similarity = SequenceMatcher(None, tldextract.extract(domain).domain, selected_tw_handle).ratio()
        # print('selected twitter handle', (selected_tw_handle, tw_similarity))

    # selecting the matched youtube channel id
    selected_yt_id = ''
    if len(yt_ids_cnt) > 1:
        yt_ids_list = sorted(list(yt_ids_cnt.keys()), key=lambda x: yt_ids_cnt[x], reverse=True)
        for yt_id in yt_ids_list:
            response = requests.get(YOUTUBE_CHANNEL_ABOUT.format(channel_id=yt_id))
            time.sleep(1)
            if match_links_on_youtube_page(response, website_url, selected_tw_handle):
                selected_yt_id = yt_id
                break
    elif len(yt_ids_cnt) == 1:
        selected_yt_id = list(yt_ids_cnt.keys())[0]
        # print('selected youtube id', selected_yt_id)

    # selecting the matched youtube channel username
    selected_yt_user = ''
    if len(yt_users_cnt) > 1:
        yt_users_list = sorted(list(yt_users_cnt.keys()), key=lambda x: yt_users_cnt[x], reverse=True)
        for yt_user in yt_users_list:
            response = requests.get(YOUTUBE_USER_ABOUT.format(user_name=yt_user))
            time.sleep(1)
            if match_links_on_youtube_page(response, website_url, selected_tw_handle):
                selected_yt_user = yt_user
                break
    elif len(yt_users_cnt) == 1:
        selected_yt_user = list(yt_users_cnt.keys())[0]
        # print('selected youtube user', selected_yt_user)

    return selected_tw_handle, tw_similarity, selected_yt_id, selected_yt_user


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

    num_media = 0
    num_found_twitter = 0
    num_found_youtube = 0
    num_fail = 0

    app_name = 'mbfc'

    with open('data/{0}/{0}_ratings_v3.csv'.format(app_name), 'w') as fout:
        with open('data/{0}/{0}_ratings_v2.csv'.format(app_name), 'r') as fin:
            fout.write('{0},{1},{2},{3},{4}\n'.format(fin.readline().rstrip(), 'TWHandle', 'TWSim', 'YTId', 'YTUser'))
            for line in fin:
                num_media += 1
                head, website_url = line.rstrip().rsplit(',', 1)
                try:
                    tw_handle, tw_sim, yt_id, yt_user = crawl_social_media_from_url(website_url, api)
                    fout.write('{0},{1},{2},{3},{4}\n'.format(line.rstrip(), tw_handle, tw_sim, yt_id, yt_user))
                    print('crawled accounts: {0:>10} | {1:>10} | {2:>10}'.format(tw_handle, yt_id, yt_user))
                    if tw_handle != '':
                        num_found_twitter += 1
                    if yt_id != '' or yt_user != '':
                        num_found_youtube += 1
                    if isinstance(tw_sim, float) and tw_sim < 0.5:
                        print('+++ Twitter handle to be reviewed: {0} {1:.4f}'.format(tw_handle, tw_sim))
                except:
                    num_fail += 1
                    continue
                print('>>> {0}/{2} twitter handles are found; {1}/{2} youtube ids'.format(num_found_twitter, num_found_youtube, num_media))

    print('in total, {0} media websites not accessible'.format(num_fail))

    timer.stop()


if __name__ == '__main__':
    main()
