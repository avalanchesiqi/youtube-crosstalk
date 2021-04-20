#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Extract temporary data for public release.

Usage: python extract_tmp_data.py
Input data files: ../data/us_polarized_videos.json.bz2,
                  ../data/us_partisan.csv
                  ../hnatt/saved_models/unseen_hnatt_prediction.csv,
                  ../prediction/all_seed_user_label.csv
Output data files: ../data/video_meta.csv,
                   ../data/hashed_user_ids.csv.bz2,
                   ../data/user_comment_meta.csv.bz2,
                   ../data/user_comment_trace.csv.bz2
Time: 1H
"""

import up  # go to root folder

import bz2, json
from collections import defaultdict, Counter

from utils.helper import Timer


def main():
    timer = Timer()
    timer.start()

    user_id_comment_ideology = defaultdict(list)
    user_id_comment_trace = defaultdict(list)

    channels = set()
    channel_leaning = {}
    channel_type = {}
    with open('data/us_partisan.csv', 'r') as fin:
        fin.readline()
        for line in fin:
            title, url, channel_title, channel_id, leaning, mtype, _ = line.rstrip().split(',', 6)
            channels.add(channel_id)
            channel_leaning[channel_id] = leaning
            channel_type[channel_id] = mtype

    channel_embed = {channel_id: idx for idx, channel_id in enumerate(list(channels))}
    embed_channel = {idx: channel_id for channel_id, idx in channel_embed.items()}

    user_leaning = {}
    with open('hnatt/saved_models/unseen_hnatt_prediction.csv', 'r') as fin:
        for line in fin:
            user_id, leaning = line.rstrip().split(',')
            user_leaning[user_id] = leaning
    with open('prediction/all_seed_user_label.csv', 'r') as fin:
        for line in fin:
            user_id, leaning = line.rstrip().split(',')
            user_leaning[user_id] = leaning

    num_video = 0
    with open('data/video_meta.csv', 'w') as fout:
        fout.write('video_id,channel_id,media_leaning,media_type,num_view,'
                   'num_comment,num_cmt_from_liberal,num_cmt_from_conservative,num_cmt_from_unknown,'
                   'num_top_comment,top_leanings\n')
        with bz2.BZ2File('data/us_polarized_videos.json.bz2', 'r') as fin:
            for line in fin:
                line = line.decode('utf-8')
                video_json = json.loads(line.rstrip())
                video_id = video_json['vid']
                channel_id = video_json['channel_id']
                num_view = video_json['view_count']
                num_comment = video_json['num_comment']

                num_cmt_from_liberal = 0
                num_cmt_from_conservative = 0
                num_cmt_from_unknown = 0
                if channel_id in channels:
                    media_ideology = channel_leaning[channel_id]
                    media_type = channel_type[channel_id]

                    comment_list = video_json.pop('comment_list')
                    for comment_card in comment_list:
                        aid = comment_card['aid']
                        if aid != '':
                            user_id_comment_ideology[aid].append(media_ideology)
                            user_id_comment_trace[aid].append(channel_embed[channel_id])

                        if aid in user_leaning:
                            if user_leaning[aid] == 'L':
                                num_cmt_from_liberal += 1
                            elif user_leaning[aid] == 'R':
                                num_cmt_from_conservative += 1
                        else:
                            num_cmt_from_unknown += 1

                    top_leanings = []
                    is_streamed = video_json['is_streamed']
                    if num_comment > 0 and not is_streamed:
                        # we ignore live stream videos because comment records on "top comments" tab are not complete
                        top_comment_list = video_json.pop('top_comment_list')
                        for comment_card in top_comment_list:
                            aid = comment_card['aid']
                            if aid in user_leaning:
                                top_leanings.append(user_leaning[aid])
                            else:
                                top_leanings.append('U')

                    num_top_comment = len(top_leanings)

                    fout.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}\n'.format(video_id,
                                                                                       channel_id,
                                                                                       media_ideology,
                                                                                       media_type,
                                                                                       num_view,
                                                                                       num_comment,
                                                                                       num_cmt_from_liberal,
                                                                                       num_cmt_from_conservative,
                                                                                       num_cmt_from_unknown,
                                                                                       num_top_comment,
                                                                                       ''.join(top_leanings)))

                    num_video += 1
                    if num_video % 10000 == 0:
                        print('>>> processed {0:,} videos'.format(num_video))

    num_user = len(user_id_comment_ideology)
    print('{0:,} users post comments on the YouTube U.S. political videos.'.format(num_user))
    print('{0:,} videos'.format(num_video))

    aid_embed = {aid: idx for idx, aid in enumerate(list(user_id_comment_ideology.keys()))}
    embed_aid = {idx: aid for aid, idx in aid_embed.items()}

    with bz2.open('data/hashed_user_ids.csv.bz2', 'at') as fout:
        fout.write('user_id,hashed_user_id\n')
        for aid_idx in range(num_user):
            fout.write('{0},{1}\n'.format(embed_aid[aid_idx], aid_idx))

    with bz2.open('data/user_comment_meta.csv.bz2', 'at') as fout:
        fout.write('hashed_user_id,predicted_user_leaning,num_comment,num_cmt_on_left,num_cmt_on_right\n')
        for aid_idx in range(num_user):
            aid = embed_aid[aid_idx]
            if aid in user_leaning:
                leaning = user_leaning[aid]
            else:
                leaning = 'U'

            comment_list = user_id_comment_ideology[aid]
            num_comment = len(comment_list)
            num_comment_left = 0
            num_comment_right = 0

            for comment_place in comment_list:
                if comment_place == 'L':
                    num_comment_left += 1
                elif comment_place == 'R':
                    num_comment_right += 1

            fout.write('{0},{1},{2},{3},{4}\n'.format(aid_idx, leaning, num_comment, num_comment_left, num_comment_right))
            if aid_idx % 100000 == 0:
                print('>>> 1 processed {0}/{1}={2:.2f}% users'.format(aid_idx, num_user, aid_idx / num_user * 100))

    with bz2.open('data/user_comment_trace.tsv.bz2', 'at') as fout:
        fout.write('hashed_user_id\tpredicted_user_leaning\tcomment_trace\n')
        for aid_idx in range(num_user):
            aid = embed_aid[aid_idx]
            if aid in user_leaning:
                leaning = user_leaning[aid]
            else:
                leaning = 'U'

            commented_channel_list = user_id_comment_trace[aid]
            sorted_channel_meta = sorted(Counter(commented_channel_list).items(), key=lambda x: x[1], reverse=True)

            to_write_list = []
            for embed, freq in sorted_channel_meta:
                to_write_list.append('{0},{1}'.format(embed_channel[embed], freq))

            fout.write('{0}\t{1}\t{2}\n'.format(aid_idx, leaning, ';'.join(to_write_list)))
            if aid_idx % 100000 == 0:
                print('>>> 2 processed {0}/{1}={2:.2f}% users'.format(aid_idx, num_user, aid_idx / num_user * 100))

    timer.stop()


if __name__ == '__main__':
    main()
