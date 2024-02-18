#!/bin/bash
mkdir youtube-trending-video-dataset

# Data collector
bash /app/data_collector/fait_auto.sh

# Data integrator
bash /app/integrator/working_y_n.sh

# Data Processor 
bash /app/processor/process.sh

# Transform and build app
python3 app.py
