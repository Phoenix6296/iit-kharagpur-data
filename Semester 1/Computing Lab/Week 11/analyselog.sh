#!/bin/bash

display_usage() {
    echo "Usage: $0 <log_file> <time_window_in_minutes>"
    exit 1
}

if [ "$#" -ne 2 ]; then
    echo "Error: Incorrect number of arguments."
    display_usage
fi

log_file="$1"
time_window_min="$2"

if [ ! -f "$log_file" ]; then
    echo "Error: Log file not found."
    exit 1
fi

if ! [[ "$time_window_min" =~ ^[0-9]+$ ]]; then
    echo "Error: Time window must be a valid integer."
    display_usage
fi

time_window_sec=$((time_window_min * 60))

parsed_log=$(mktemp)

awk '{print $1, $2, $3}' "$log_file" | sed 's/\[//;s/\]//' > "$parsed_log"

get_epoch_time() {
    date -jf "%Y-%m-%d %H:%M:%S" "$1" "+%s"
}

convert_epoch_to_date() {
    date -r "$1" "+%Y-%m-%d %H:%M:%S"
}

max_entries=0
start_time=""
end_time=""
ip_array=()

while read -r log_entry; do
    timestamp=$(echo "$log_entry" | awk '{print $1 " " $2}')
    ip=$(echo "$log_entry" | awk '{print $3}')

    current_epoch_time=$(get_epoch_time "$timestamp")
    window_end_epoch_time=$((current_epoch_time + time_window_sec))

    window_entry_count=0
    temp_ip_array=()

    while read -r inner_entry; do
        inner_timestamp=$(echo "$inner_entry" | awk '{print $1 " " $2}')
        inner_ip=$(echo "$inner_entry" | awk '{print $3}')
        inner_epoch_time=$(get_epoch_time "$inner_timestamp")

        if [[ "$inner_epoch_time" -ge "$current_epoch_time" && "$inner_epoch_time" -le "$window_end_epoch_time" ]]; then
            ((window_entry_count++))
            temp_ip_array+=("$inner_ip")
        fi
    done < "$parsed_log"

    if [[ "$window_entry_count" -gt "$max_entries" ]]; then
        max_entries=$window_entry_count
        start_time=$timestamp
        end_time=$(convert_epoch_to_date "$window_end_epoch_time")
        ip_array=("${temp_ip_array[@]}")
    fi
done < "$parsed_log"

if [ "$max_entries" -gt 0 ]; then
    sorted_ips=$(echo "${ip_array[@]}" | tr ' ' '\n' | sort | uniq -c | sort -rn | head -3)
else
    sorted_ips=""
fi

echo "Start Time: $start_time"
echo "End Time: $end_time"
echo "Number of Entries: $max_entries"
echo "Top 3 IPs in the window:"

echo "$sorted_ips" | awk '{print "    " $2 " - " $1}'

rm "$parsed_log"
