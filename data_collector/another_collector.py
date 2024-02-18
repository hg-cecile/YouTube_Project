import kaggle

kaggle.api.authenticate()

dataset_url = 'rsrishav/youtube-trending-video-dataset'
file_name1 = 'FR_youtube_trending_data.csv'
file_name2 = 'FR_category_id.json'

kaggle.api.dataset_download_file(dataset_url, file_name1, path='.')
kaggle.api.dataset_download_file(dataset_url, file_name2, path='.')
