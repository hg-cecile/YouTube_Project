#!/bin/bash
FILE1="/app/FR_youtube_trending_data.csv"
FILE2="/app/FR_category_id.json"
dt=$(date +%Y-%m-%d-%H-%M-%S)

check_file_permissions() {
  local file="$1"
  
  if [ -e "$file" ]; then
    echo "$file exists."
    
    if [ -r "$file" ] && [ -w "$file" ]; then
      echo "You have read and write permissions on $file."
    else
      echo "You don't have sufficient permissions to read or write on $file."

    fi
  else
    echo "$file does not exist."
    bash /app/data_collector/fait_auto.sh
  fi
}

check_file_permissions "$FILE1"
check_file_permissions "$FILE2"

