# -*- coding: utf-8 -*-

import sys, os, time
import lxml.html
from lxml.cssselect import CSSSelector

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from utils.crawlers import YOUTUBE_COMMENTS_AJAX_URL_OLD, YOUTUBE_COMMENTS_AJAX_URL_NEW
from utils.crawlers import ajax_request, search_dict


def download_comments_top(session, session_token, ncd, top=False, sleep=0.2):
    # sorted by "Top comments"
    comment_list = []
    num_request = 1

    visited_continuations = set()
    if ncd is not None:
        if 'continuation' in ncd and 'clickTrackingParams' in ncd:
            continuations = [(ncd['continuation'], ncd['clickTrackingParams'])]

            while continuations:
                continuation, itct = continuations.pop()
                if continuation in visited_continuations:
                    break
                response_json = ajax_request(session, YOUTUBE_COMMENTS_AJAX_URL_NEW,
                                             params={'action_get_comments': 1,
                                                     'pbj': 1,
                                                     'ctoken': continuation,
                                                     'continuation': continuation,
                                                     'itct': itct},
                                             data={'session_token': session_token},
                                             headers={'X-YouTube-Client-Name': '1',
                                                      'X-YouTube-Client-Version': '2.20200207.03.01'})
                num_request += response_json['num_request']

                if 'error' in response_json:
                    raise Exception(response_json['error'])
                if next(search_dict(response_json, 'externalErrorMessage'), None):
                    if next(search_dict(response_json, 'code')) == 'INVALID_VALUE':
                        raise Exception('Comments are turned off')
                    else:
                        raise Exception('Error returned from server: ' + next(search_dict(response_json, 'externalErrorMessage')))

                if not top:
                    # Ordering matters. The newest continuations should go first.
                    continuations = [(ncd['continuation'], ncd['clickTrackingParams'])
                                     for ncd in search_dict(response_json, 'nextContinuationData')] + continuations

                for comment in search_dict(response_json, 'commentRenderer'):
                    try:
                        votes_text = comment.get('voteCount', {}).get('simpleText', '0')
                        try:
                            votes = int(votes_text)
                        except:
                            if 'K' in votes_text:
                                votes = int(1000 * float(votes_text[:-1]))
                            elif 'M' in votes_text:
                                votes = int(1000000 * float(votes_text[:-1]))
                            else:
                                votes = 0

                        comment_obj = {'cid': comment['commentId'],
                                       'text': ''.join([c['text'] for c in comment['contentText']['runs']]),
                                       'time': comment['publishedTimeText']['runs'][0]['text'],
                                       'author': comment.get('authorText', {}).get('simpleText', ''),
                                       'aid': comment.get('authorEndpoint', {}).get('browseEndpoint', {}).get('browseId', ''),
                                       'votes': votes}
                        comment_list.append(comment_obj)
                    except:
                        pass

                visited_continuations.add(continuation)
                time.sleep(sleep)
    return comment_list, num_request


def download_comments_time(session, video_id, session_token, sleep=0.2):
    # sorted by "Newest first"
    comment_list = []
    num_request = 1

    # Use the old youtube API to download all comments (does not work for live streams)
    # collected comment ids
    ret_cids = set()
    page_token = ''
    first_iteration = True

    # Get remaining comments (the same as pressing the 'Show more' button)
    while page_token or first_iteration:
        data = {'video_id': video_id,
                'session_token': session_token}

        params = {'action_load_comments': 1,
                  'order_by_time': True,
                  'filter': video_id}

        if first_iteration:
            params['order_menu'] = True
        else:
            data['page_token'] = page_token

        response_json = ajax_request(session, YOUTUBE_COMMENTS_AJAX_URL_OLD,
                                     params=params,
                                     data=data)
        num_request += response_json['num_request']

        if 'error' in response_json:
            raise Exception(response_json['error'])

        page_token, html = response_json.get('page_token', None), response_json['html_content']

        for comment_obj in extract_comments(html):
            if comment_obj['cid'] not in ret_cids:
                ret_cids.add(comment_obj['cid'])
                comment_list.append(comment_obj)

        first_iteration = False
        time.sleep(sleep)
    return comment_list, num_request


def extract_comments(html):
    tree = lxml.html.fromstring(html)
    item_sel = CSSSelector('.comment-item')
    text_sel = CSSSelector('.comment-text-content')
    time_sel = CSSSelector('.time')
    author_sel = CSSSelector('.user-name')
    vote_sel = CSSSelector('.like-count.off')

    for item in item_sel(tree):
        if len(vote_sel(item)) > 0:
            votes_text = vote_sel(item)[0].text_content()
            try:
                votes = int(votes_text)
            except:
                if 'K' in vote_sel(item)[0].text_content():
                    votes = int(1000 * float(votes_text[:-1]))
                elif 'M' in vote_sel(item)[0].text_content():
                    votes = int(1000000 * float(votes_text[:-1]))
                else:
                    votes = 0
        else:
            votes = 0

        yield {'cid': item.get('data-cid'),
               'text': text_sel(item)[0].text_content(),
               'time': time_sel(item)[0].text_content().strip(),
               'author': author_sel(item)[0].text_content(),
               'aid': author_sel(item)[0].get('href').strip('/channel/'),
               'votes': votes}
