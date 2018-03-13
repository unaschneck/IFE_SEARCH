#!/bin/bash
# run for each file in the directory in order
DIRECTORY_FOLDER=$1 
#echo $DIRECTORY_FOLDER
for text_file in `ls $DIRECTORY_FOLDER`
do
    python ife_processing.py -F $DIRECTORY_FOLDER$text_file
    #echo "$DIRECTORY_FOLDER$text_file"
    echo ""
done

