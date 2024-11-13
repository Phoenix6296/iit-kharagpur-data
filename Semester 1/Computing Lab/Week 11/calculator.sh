#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Error: Must pass exactly 3 arguments"
    exit 1
fi

num1=$1
operator=$2
num2=$3

case $operator in
    +)
        result=$(echo "$num1 + $num2" | bc)
        ;;
    -)
        result=$(echo "$num1 - $num2" | bc)
        ;;
    \*)
        result=$(echo "$num1 * $num2" | bc)
        ;;
    /)
        if [ "$num2" == "0" ]; then
            echo "Error: Division by zero is not allowed"
            exit 1
        fi
        result=$(echo "scale=4; $num1 / $num2" | bc)
        result=$(echo "scale=2; ($result + 0.005)/1" | bc) 
        ;;
    *)
        echo "Error: Invalid operator. Use one of +, -, *, /"
        exit 1
        ;;
esac

printf "%.2f\n" "$result"