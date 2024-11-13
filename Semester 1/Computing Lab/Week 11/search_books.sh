#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <input_file> <search_phrase> <context_type> <context_words>"
    exit 1
fi

source_file="$1"
target_phrase="$2"
context_option="$3"
num_context_words="$4"

if [ ! -f "$source_file" ]; then
    echo "Error: File '$source_file' not found!"
    exit 1
fi

if [[ "$context_option" != "-before" && "$context_option" != "-after" && "$context_option" != "-both" ]]; then
    echo "Error: Invalid context type. Use -before, -after, or -both."
    exit 1
fi

target_phrase_lower=$(echo "$target_phrase" | tr '[:upper:]' '[:lower:]')

get_context() {
    local word_array=("$@")  
    local match_index=$1 
    local total_words=${#word_array[@]}  
    local context_count=$2 

    start=$((match_index - context_count))
    [ $start -lt 0 ] && start=0
    context_before="${word_array[@]:$start:$((match_index - start))}"

    end=$((match_index + context_count))
    [ $end -gt $total_words ] && end=$total_words
    context_after="${word_array[@]:$((match_index + 1)):$context_count}"

    case "$context_option" in
        -before) echo "$context_before";;
        -after) echo "$context_after";;
        -both) echo "$context_before ... $context_after";;
    esac
}

while IFS="|" read -r book_title book_author publication_year book_summary; do
    summary_lower=$(echo "$book_summary" | tr '[:upper:]' '[:lower:]')

    if grep -q "$target_phrase_lower" <<< "$summary_lower"; then
        IFS=' ' read -r -a word_array <<< "$book_summary"

        for i in "${!word_array[@]}"; do
            if [[ "${word_array[$i],,}" == *"$target_phrase_lower"* ]]; then
                phrase_index=$i
                break
            fi
        done

        context=$(get_context "$phrase_index" "$num_context_words" "${word_array[@]}")

        echo "Book: $book_title | Author: $book_author"
        echo "Context: ...$context..."
    fi
done < "$source_file"
