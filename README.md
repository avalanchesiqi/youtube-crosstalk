# Code and Data for YouTube Cross-Talk Study

We release the code and data for the following paper.
If you use these datasets, or refer to our findings, please cite:
> [Siqi Wu](https://avalanchesiqi.github.io/) and [Paul Resnick](https://www.si.umich.edu/people/paul-resnick). Cross-Partisan Discussions on YouTube: Conservatives Talk to Liberals but Liberals Don't Talk to Conservatives. *AAAI International Conference on Weblogs and Social Media (ICWSM)*, 2021. \[[paper](https://avalanchesiqi.github.io/files/icwsm2021crosstalk.pdf)\|[slides](https://avalanchesiqi.github.io/files/icwsm2021slides.pdf)\|[poster](https://avalanchesiqi.github.io/files/icwsm2021poster.pdf)\]

## Data
The data is hosted on [Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/KF5JC5).
See more details in this [data description](/data/README.md).

## Plots
Plots reported in the paper can be reproduced by the scripts in [plots](/plots) directory, 
with the aggregate video/user data we provide in [data](/data) directory as input files.

## Scrapers
The [crawler](/crawler) directory contains all scripts for building our data collection pipeline.
You will need to first copy [conf.py](/conf/conf.py) to [local_conf.py](/conf/local_conf.py), then set up the Twitter and YouTube credentials.

## Obtaining political leaning for seed users
The [prediction](/prediction) directory contains all scripts for estimating the political leaning labels for seed users.

## Pre-trained Hierarchical Attention Network (HAN)
The [HAN model](/hnatt) we built was modified from the inspiring code from [hnatt](https://github.com/minqi/hnatt).
See [this](/hnatt/README.md) for how to use our pre-trained HAN models for predicting user political leaning given a set of comments.

## Python version
The HAN module was tested in Python 2.7.
Other than that, all other codes were developed and tested in Python 3.7.
See more details in the [requirements.txt](/requirements.txt).