# Data for YouTube Cross-Partisanship Discussions Study

These datasets are first used in the following paper.
If you use these datasets, or refer to our findings, please cite:
> [Siqi Wu](https://avalanchesiqi.github.io/) and [Paul Resnick](https://www.si.umich.edu/people/paul-resnick). Cross-Partisan Discussions on YouTube: Conservatives Talk to Liberals but Liberals Don't Talk to Conservatives. *AAAI International Conference on Weblogs and Social Media (ICWSM)*, 2021. \[[paper](https://avalanchesiqi.github.io/files/icwsm2021crosstalk.pdf)\]

## Data collection
These datasets are collected via a series of scraping scripts, see [crawler](/crawler) for details.

## Data
The data is hosted on [Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/KF5JC5).

## File Descriptions

### `us_partisan.csv`
Metadata for 1,267 US partisan media on YouTube.
The first row is header.
Fields include 
```csv
title, url, channel_title, channel_id, leaning, type, source, channel_description
```

### `video_meta.csv`
Metadata for 274241 YouTube political videos from US partisan media.
The first row is header.
Fields include 
```csv
video_id, channel_id, media_leaning, media_type, num_view, num_comment, num_cmt_from_liberal, num_cmt_from_conservative, num_cmt_from_unknown
```

### `user_comment_meta.csv.bz2`
Metadata for 9,304,653 YouTube users who have commented on YouTube political videos. 
The first row is header. 
Fields include 
```csv
hashed_user_id, predicted_user_leaning, num_comment, num_cmt_on_left, num_cmt_on_right
```

### `user_comment_trace.tsv.bz2`
Comment trace for 9,304,653 YouTube users who have commented on YouTube political videos.
The first row is header.
Fields include `hashed_user_id   predicted_user_leaning  comment_trace` (split by \t)
`comment_trace` consists of 
`channel_id1,num_comment_on_this_channel1;channel_id2,num_comment_on_this_channel2;...` (split by ;)