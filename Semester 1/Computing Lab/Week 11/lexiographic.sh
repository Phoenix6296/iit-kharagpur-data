#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_directory> <output_directory>"
    exit 1
fi

source_directory=$1
destination_directory=$2

if [ ! -d "$source_directory" ]; then
    echo "Error: Input directory '$source_directory' not found."
    exit 1
fi

if [ ! -d "$destination_directory" ]; then
    mkdir -p "$destination_directory"
fi

for letter in {A..Z}; do
    output_file="$destination_directory/$letter.txt"
    touch "$output_file"
done

for input_file in "$source_directory"/*.txt; do
    if [ -f "$input_file" ]; then
        while IFS= read -r name; do
            
            if [ -z "$name" ]; then
                continue
            fi
            
            initial_letter=$(echo "${name:0:1}" | tr '[:lower:]' '[:upper:]')
            
            if [[ "$initial_letter" =~ [A-Z] ]]; then
                echo "$name" >> "$destination_directory/$initial_letter.txt"
            fi
        done < "$input_file"
    fi
done

for letter in {A..Z}; do
    output_file="$destination_directory/$letter.txt"
    sort -o "$output_file" "$output_file"
done

echo "Names have been processed and sorted into files."
