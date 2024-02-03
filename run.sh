#!/bin/bash
mkdir youtube-trending-video-dataset

# Data collector
bash /app/data_collector/fait_auto.sh

# moving data
mv /app/FR_youtube_trending_data.csv /app/youtube-trending-video-dataset/FR_youtube_trending_data.csv
mv /app/FR_category_id.json /app/youtube-trending-video-dataset/FR_category_id.json

# Data integrator should be there
###
#
#
###


python3 app_yt.py
