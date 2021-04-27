# Data for YouTube Cross-Partisanship Discussions Study

These datasets are first used in the following paper.
If you use these datasets, or refer to our findings, please cite:
> [Siqi Wu](https://avalanchesiqi.github.io/) and [Paul Resnick](https://www.si.umich.edu/people/paul-resnick). Cross-Partisan Discussions on YouTube: Conservatives Talk to Liberals but Liberals Don't Talk to Conservatives. *AAAI International Conference on Weblogs and Social Media (ICWSM)*, 2021. \[[paper](https://avalanchesiqi.github.io/files/icwsm2021crosstalk.pdf)\]

## Data collection
These datasets are collected via a series of scraping scripts, see [crawler](/crawler) for details.

## Data
The data is hosted on [Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/KF5JC5).

### Content
| filename | description |
| ---: | :--- |
| `us_partisan.csv` | Metadata for 1,267 US partisan media on YouTube |
| `video_meta.csv` | Metadata for 274,241 YouTube political videos from US partisan media |
| `user_comment_meta.csv.bz2` | Metadata for 9,304,653 YouTube users who have commented on YouTube political videos |
| `user_comment_trace.tsv.bz2` | Comment trace for 9,304,653 YouTube users who have commented on YouTube political videos |
| `trained_HAN_models.tar.bz2` | 5 trained HAN models for predicting user political leanings |

#### `us_partisan.csv`
Metadata for 1,267 US partisan media on YouTube.
The first row is header.
It can be viewed on this [Google Sheet](https://docs.google.com/spreadsheets/d/1Hl-1-ryJEM9QLHAeBztMtq_dIEvm5dad0eZ4mAP8Y4s/edit?usp=sharing).
Fields include 
```csv
title, url, channel_title, channel_id, leaning, type, source, channel_description
```

#### `video_meta.csv`
Metadata for 274,241 YouTube political videos from US partisan media.
The first row is header.
Fields include 
```csv
video_id, channel_id, media_leaning, media_type, num_view, num_comment, num_cmt_from_liberal, num_cmt_from_conservative, num_cmt_from_unknown
```

#### `user_comment_meta.csv.bz2`
Metadata for 9,304,653 YouTube users who have commented on YouTube political videos. 
The first row is header. 
Fields include 
```csv
hashed_user_id, predicted_user_leaning, num_comment, num_cmt_on_left, num_cmt_on_right
```

#### `user_comment_trace.tsv.bz2`
Comment trace for 9,304,653 YouTube users who have commented on YouTube political videos.
The first row is header.
Fields include `hashed_user_id   predicted_user_leaning  comment_trace` (split by \t)
`comment_trace` consists of 
`channel_id1,num_comment_on_this_channel1;channel_id2,num_comment_on_this_channel2;...` (split by ;)

For example, 
```tsv
99998   R       UCwWhs_6x42TyRM4Wstoq8HA,25;UCXIJgqnII2ZOINSWNOGFThA,20;UCWXPkK02j6MHW-4xCJzgMuw,17;UC-SJ6nODDmufqBzPBwCvYvQ,5;UCJg9wBPyKMNA5sRDnvzmkdg,2;UCupvZG-5ko_eiXAupbDfxWw,2;UCKgJEs_v0JB-6jWb8lIy9Xw,1;UCNZyLULUQBp5e9Q1cKtvk6Q,1;UCBi2mrWuNuyYy4gbM6fU18Q,1
```
It means user 99998 is predicted to lean conservative, they have posted 25 comments on `UCwWhs_6x42TyRM4Wstoq8HA`, 20 comments on `UCXIJgqnII2ZOINSWNOGFThA`, etc.

#### `trained_HAN_models.tar.bz2`
Five trained HAN models for predicting user political leanings.
Each model consists a `.h5` model file and `.tokenizer` tokenizer file.
See [this](/hnatt/README.md) for how to use our pre-trained HAN models.
