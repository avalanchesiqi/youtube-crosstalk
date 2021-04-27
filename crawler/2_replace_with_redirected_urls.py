#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Correcting the redirected URLs so that we can disable redirected when scraping for social media account.
For example, it should be https://www.businessinsider.com rather than https://www.businessinsider.com.au.
The national-version website may operate a different social media account.
When the script is completed, manually address conflict by examining the OrigURL column.
The OrigURL column should be removed after conflict solved.

Usage: python 2_replace_with_redirected_urls.py
Input data files: data/mbfc/mbfc_ratings_v1.csv
Output data files: data/mbfc/mbfc_ratings_v2.csv
"""

import up  # go to root folder

import requests, random

from utils.crawlers import USER_AGENT_LIST
from utils.crawlers import get_domain, format_url


def main():
    app_name = 'mbfc'

    with open('data/{0}/{0}_ratings_v2.csv'.format(app_name), 'w') as fout:
        with open('data/{0}/{0}_ratings_v1.csv'.format(app_name), 'r') as fin:
            fout.write('{0},{1}\n'.format(fin.readline().rstrip(), 'OrigURL'))
            for line in fin:
                head, website_url, domain = line.rstrip().rsplit(',', 2)
                title = head.split(',')[0]
                try:
                    response = requests.get(website_url,
                                            headers={'User-Agent': random.choice(USER_AGENT_LIST)},
                                            allow_redirects=True)
                    redirected_url = response.url
                    if get_domain(website_url) == get_domain(redirected_url):
                        fout.write('{0},{1}\n'.format(head, format_url(redirected_url)))
                        print('matched {0}, {1}'.format(title, format_url(redirected_url)))
                    else:
                        fout.write('{0},{1},{2}\n'.format(head, format_url(redirected_url), website_url))
                        print('>>> NOT matched! {0}, {1}, {2}'.format(title, format_url(redirected_url), website_url))
                except:
                    pass


if __name__ == '__main__':
    main()
