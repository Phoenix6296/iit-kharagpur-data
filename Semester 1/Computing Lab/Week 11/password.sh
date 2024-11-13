#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Please provide exactly one number as an argument."
    exit 1
fi
if [ -z "$1" ] || [ "$1" -lt 4 ]; then
  echo "Usage: $0 <length>"
  echo "Password length must be 4 or greater."
  exit 1
fi

LENGTH=$1

shuffle() {
  echo "$1" | fold -w1 | shuf | tr -d '\n'
}

UPPER=$(tr -dc 'A-Z' < /dev/urandom | head -c1)
LOWER=$(tr -dc 'a-z' < /dev/urandom | head -c1)
DIGIT=$(tr -dc '0-9' < /dev/urandom | head -c1)
SPECIAL=$(tr -dc '!@#$%^&*()+' < /dev/urandom | head -c1)

REMAINING=$(tr -dc 'A-Za-z0-9!@#$%^&*()+' < /dev/urandom | head -c $(($LENGTH - 4)))

PASSWORD="$UPPER$LOWER$DIGIT$SPECIAL$REMAINING"

PASSWORD=$(shuffle "$PASSWORD")

echo "Generated password: $PASSWORD"
