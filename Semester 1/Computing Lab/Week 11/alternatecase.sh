#!/bin/bash

alternate_case() {
    local input_text="$1"
    local output_text=""
    local toggle=1  

    for (( i=0; i<${#input_text}; i++ )); do
        current_char="${input_text:$i:1}"
        
        if [[ "$current_char" =~ [a-zA-Z] ]]; then
            if [[ $toggle -eq 1 ]]; then
                output_text+=$(echo "$current_char" | tr '[:lower:]' '[:upper:]')
                toggle=0
            else
                output_text+=$(echo "$current_char" | tr '[:upper:]' '[:lower:]')
                toggle=1
            fi
        else
            output_text+="$current_char"
        fi
    done

    echo "$output_text"
}

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_file> <search_word>"
    exit 1
fi

input_file="$1"
search_term="$2"

if [ ! -f "$input_file" ]; then
    echo "Error: File '$input_file' not found!"
    exit 1
fi

search_term_lower=$(echo "$search_term" | tr '[:upper:]' '[:lower:]')

while IFS= read -r current_line || [[ -n "$current_line" ]]; do  
    current_line_lower=$(echo "$current_line" | tr '[:upper:]' '[:lower:]')

    if echo "$current_line_lower" | grep -q "$search_term_lower"; then
        modified_line=$(alternate_case "$current_line")
        echo "$modified_line"
    else
        echo "$current_line"
    fi
done < "$input_file"
