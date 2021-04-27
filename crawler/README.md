# Data Collection Pipeline

filename | usage
---: | :--- 
[`1_scrape_mbfc_ratings.py`](1_scrape_mbfc_ratings.py) | Scrape the MediaBiasFactCheck media ratings
[`2_replace_with_redirected_urls.py`](2_replace_with_redirected_urls.py) | Given a URL, query it and get the redirected URL
[`3_scrape_media_website.py`](3_scrape_media_website.py) | Scrape a news website for social media (Twitter + YouTube) accounts
[`4_search_twitter_handle.py`](4_search_twitter_handle.py) | Search for the unresolved Twitter accounts by querying Twitter search API with media titles
[`5_search_youtube_channel.py`](5_search_youtube_channel.py) | Search for the unresolved YouTube channels by searching site title on YouTube
[`6_get_channel_id.py`](6_get_channel_id.py) | Given a channel username, get YouTube channel id or validate the id
[`7_fetch_youtube_videos_playlist.py`](7_fetch_youtube_videos_playlist.py) | Given a channel id, fetching its YouTube videos
[`8_filter_by_video_upload_time.py`](8_filter_by_video_upload_time.py) | Keep video ids if they are uploaded between 2020-01-01 and 2020-08-31
[`9_scrape_youtube_video_metadata.py`](9_scrape_youtube_video_metadata.py) | Given a channel id, fetch YouTube video metadata
[`10_scrape_youtube_subscriptions.py`](10_scrape_youtube_subscriptions.py) | Given a channel id, fetch user description and subscriptions
[`11_scrape_youtube_featured_channels.py`](11_scrape_youtube_featured_channels.py) | Given a channel id, fetch user featured channels
