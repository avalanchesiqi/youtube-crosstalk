#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Scraping the MediaBiasFactCheck media ratings.
https://mediabiasfactcheck.com/{page}
page = [left,leftcenter,center,right-center,right,fake-news]

Usage: python 1_scrape_mbfc_ratings.py
Output data files: ../data/mbfc/mbfc_ratings_v1.csv
"""

import up  # go to root folder
import time, requests, re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from utils.crawlers import MBFC_SOURCE_URL


def get_domain(url):
    domain = urlparse(url).netloc
    if domain.startswith('www.'):
        domain = domain[len('www.'):]
    return domain


def main():
    fout = open('data/mbfc/mbfc_ratings_v1.csv', 'w')
    fout.write('Title,Category,Img,Country,URL,Domain\n')

    ideology_pages = ['left', 'leftcenter', 'center', 'right-center', 'right', 'fake-news']
    ideology_labels = ['left', 'center-left', 'center', 'center-right', 'right', 'fake-news']
    for ideology_page, ideology_label in zip(ideology_pages, ideology_labels):
        response = requests.get(MBFC_SOURCE_URL.format(page=ideology_page))
        soup = BeautifulSoup(response.text, 'lxml')
        page_table = soup.find('table', {'id': 'mbfc-table'}).find_all('tr')
        for page in page_table:
            try:
                # getting the information for each website
                page = page.find('a', href=True).get('href')

                response2 = requests.get(MBFC_SOURCE_URL.format(page=page))
                html = re.sub(r'<br>|<p>|</p>', '\n', response2.text)
                soup2 = BeautifulSoup(html, 'lxml')
                source_title = soup2.find('h1', {'class': 'page-title'}).text
                # remove dash, comma, and consecutive spaces
                source_title = re.sub('[+,-]', '', source_title).strip()
                print('source title:', source_title)
                print('source ideology:', ideology_label)

                ideology_img = soup2.find_all('img')
                img_filename = ''
                for img in ideology_img:
                    img_url = img.get('data-orig-file')
                    if img_url:
                        if 'mediabiasfactcheck.com/wp-content/uploads/2016/12' in img_url:
                            img_filename = img_url.rsplit('/', 1)[1].split('?', 1)[0]
                            print('ideology img:', img_filename)
                            break

                country = 'NA'
                website_url = 'NA'
                domain = 'NA'
                for line in soup2.text.split('\n'):
                    country_pattern = r'Country:\s[a-zA-Z]+'
                    source_pattern = r'Sources?:\shttps?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
                    if bool(re.match(country_pattern, line)):
                        country = line.rstrip().split(':')[1].split('(')[0].strip()
                        if country == 'Unknown':
                            country = 'NA'
                    elif bool(re.match(source_pattern, line)):
                        website_url = line.rstrip().split(':', 1)[1].strip()
                        domain = get_domain(website_url)
                print('country:', country)
                print('website url:', website_url)
                print('domain:', domain)

                fout.write('{0},{1},{2},{3},{4},{5}\n'
                           .format(source_title, ideology_label, img_filename,
                                   country, website_url, domain))
                print()
                time.sleep(1)
            except Exception as e:
                print('>>> failed crawling with messages:', str(e))
                continue

    fout.close()


if __name__ == '__main__':
    main()
