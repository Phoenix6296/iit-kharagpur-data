#!/bin/bash

calculate_gcd() {
    local first_num=$1
    local second_num=$2
    while [ $second_num -ne 0 ]; do
        local temp=$second_num
        second_num=$((first_num % second_num))
        first_num=$temp
    done
    echo $first_num
}

calculate_lcm() {
    local first_num=$1
    local second_num=$2
    local gcd_result=$(calculate_gcd $first_num $second_num)
    echo $((first_num * second_num / gcd_result))
}

if [ $# -ne 1 ]; then
    echo "Usage: $0 <file>"
    exit 1
fi

input_file=$1
number_list=$(cat "$input_file")

lcm_final=0
for current_number in $number_list; do
    if [ $lcm_final -eq 0 ]; then
        lcm_final=$current_number
    else
        lcm_final=$(calculate_lcm $lcm_final $current_number)
    fi
done

echo "LCM: $lcm_final"
