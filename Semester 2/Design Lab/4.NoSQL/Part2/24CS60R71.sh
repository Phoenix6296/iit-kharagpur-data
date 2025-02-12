DATA_DIR="./data"
INTERMEDIATE_FILE="intermediate.txt"
OUTPUT_FILE="result__.txt"

> "$INTERMEDIATE_FILE"

for file in "$DATA_DIR"/*.txt; do
    echo "Processing file: $file"
    python mapper.py "$file" | sort | python combiner.py >> "$INTERMEDIATE_FILE" &
done

wait

sort -n "$INTERMEDIATE_FILE"|python reducer.py > "$OUTPUT_FILE"

rm "$INTERMEDIATE_FILE"