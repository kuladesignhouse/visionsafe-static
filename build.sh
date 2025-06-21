#!/bin/bash

# Run the Gulp task
gulp

# Check if the Gulp task was successful
if [ $? -eq 0 ]; then
    # Transfer the file to the server using scp
    scp ./dist/g500-video.html brgr@visionsafe.com:/home/brgr/visionsafe.com/g500-video/index.html

    # Check if the file transfer was successful
    if [ $? -eq 0 ]; then
        echo "File transferred successfully."
        afplay /System/Library/Sounds/Purr.aiff
    else
        echo "File transfer failed."
    fi
else
    echo "Gulp task failed."
fi

