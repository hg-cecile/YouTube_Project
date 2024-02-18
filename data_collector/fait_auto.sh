#!/bin/bash
mkdir /root/.kaggle

echo "collector module Starting !"
echo "moving credential from env to root"

mv /app/.env/kaggle.json /root/.kaggle/kaggle.json

echo "done moving, starting collect"
python3 /app/data_collector/another_collector.py

echo "done collecting, unpacking data !"
unzip FR_youtube_trending_data.csv.zip
echo "done unzipping !"
