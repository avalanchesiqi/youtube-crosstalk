#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Code usage of Jigsaw's perspective api.

Usage: python call_perspective.py
"""

import time, json, requests

JIGSAW_URL = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={api_key}'


def main():
    # follow the this guide to create your key
    # https://developers.perspectiveapi.com/s/docs-get-started
    api_key = 'input your perspective API key'

    comment_text = 'Why should we give her the benefit of the doubt? Clearly her appointment is driven by politics, not respect for the process'

    request_dict = {
        'comment': {'text': comment_text},
        'requestedAttributes': {'TOXICITY': {}}
    }

    response = requests.post(url=JIGSAW_URL.format(api_key=api_key), data=json.dumps(request_dict))
    while response.status_code == 429:
        time.sleep(60)
        response = requests.post(url=JIGSAW_URL.format(api_key=api_key), data=json.dumps(request_dict))

    response_dict = json.loads(response.content)
    try:
        toxicity = response_dict['attributeScores']['TOXICITY']['summaryScore']['value']
        label = 'toxic' if toxicity >= 0.7 else 'not toxic'
        print(f'Perspective API classifies this comment as {label}, the returned score is {toxicity}')
    except:
        if response.status_code == 400:
            print(response_dict['error']['message'])
        else:
            print(response_dict)
        toxicity = 'na'
        print('unsupported language or request error')


if __name__ == '__main__':
    main()