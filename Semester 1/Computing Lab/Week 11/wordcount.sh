#!/bin/bash

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <file> <word>"
  exit 1
fi

file_path="$1"
target_word="$2"

if [ ! -f "$file_path" ]; then
  echo "Error: File '$file_path' not found!"
  exit 1
fi

line_count=$(wc -l < "$file_path")
word_count=$(wc -w < "$file_path")
char_count=$(wc -m < "$file_path")
frequency_count=$(grep -o -i "\\b$target_word\\b" "$file_path" | wc -l)

# Output the results
echo "Total Lines: $line_count"
echo "Total Words: $word_count"
echo "Total Characters: $char_count"
echo "Frequency of word '$target_word': $frequency_count"
