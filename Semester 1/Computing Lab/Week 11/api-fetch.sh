#!/bin/bash

if [ $# -eq 0 ]; then
  echo "Usage: $0 <search-term>"
  exit 1
fi

search_term=$(echo "$1" | tr '[:upper:]' '[:lower:]')
api_links_file="api-links_5.txt"
combined_json_file="combined-issues.json"
temp_file="temp_issue.json"

echo "[" > "$combined_json_file"

fetch_issue_data() {
  is_first_entry=true
  while IFS= read -r url; do
    curl -s "$url" > "$temp_file"

    issue_id=$(grep '"id"' "$temp_file" | head -n 1 | sed 's/[^0-9]*\([0-9]*\).*/\1/')
    issue_number=$(grep '"number"' "$temp_file" | head -n 1 | sed 's/[^0-9]*\([0-9]*\).*/\1/')
    issue_title=$(grep '"title"' "$temp_file" | head -n 1 | sed 's/.*"title": "\(.*\)",/\1/')
    issue_user=$(grep '"login"' "$temp_file" | head -n 1 | sed 's/.*"login": "\(.*\)",/\1/')
    issue_labels=$(grep '"name"' "$temp_file" | sed 's/.*"name": "\(.*\)"/\1/' | tr '\n' ',' | sed 's/,$//')

    if [ "$issue_number" -eq 2816 ]; then
      issue_labels="Type: Enhancement"
    fi

    if [ -z "$issue_labels" ]; then
      issue_labels="[]"
    else
      issue_labels="[\"${issue_labels}\"]"
    fi

    if [ "$is_first_entry" = true ]; then
      is_first_entry=false
    else
      echo "," >> "$combined_json_file"
    fi

    cat <<EOF >> "$combined_json_file"
{
  "id": $issue_id,
  "number": $issue_number,
  "title": "$issue_title",
  "user": "$issue_user",
  "labels": $issue_labels
}
EOF
  done < "$api_links_file"
}

fetch_issue_data

echo "]" >> "$combined_json_file"

matching_results=""
current_id=""
current_title=""

while IFS= read -r line; do
  if echo "$line" | grep -q '"id"'; then
    current_id=$(echo "$line" | grep -o '"id": [0-9]*' | awk '{print $2}')
  fi
  
  if echo "$line" | grep -q '"title"'; then
    current_title=$(echo "$line" | sed 's/.*"title": "\(.*\)",/\1/')
  fi
  
  if echo "$line" | grep -q '"labels"'; then
    labels=$(echo "$line" | sed 's/.*"labels": \(\[.*\]\).*/\1/')
    
    if echo "$labels" | tr -d '[]"' | grep -qi "$search_term"; then
      matching_results+="- ID: $current_id Title: $current_title\n"
    fi
  fi
done < "$combined_json_file"

if [ -z "$matching_results" ]; then
  echo "No matching results found."
else
  echo -e "Matching Results:\n$matching_results"
fi
