import os
import csv
import re
import sys

# Increase CSV field size limit to avoid "_csv.Error: field larger than field limit"
csv.field_size_limit(sys.maxsize)

BASE_DIR = os.getcwd()
EXTRACTED_CSV_DIR = os.path.join(BASE_DIR, "Extracted_CSV")
MASKED_CSV_PATH = os.path.join(BASE_DIR, "masked_data.csv")

# Regex pattern to match function definitions
FUNC_PATTERN = re.compile(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")

# Replaces function names with MASKED_FUNCTION
def mask_function_names(code):
    return FUNC_PATTERN.sub("def MASKED_FUNCTION(", code)

# Reads CSV files, masks function names, and appends data to a single CSV
def process_csv_files():
    with open(MASKED_CSV_PATH, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["Filename", "Code"])

        for csv_file in os.listdir(EXTRACTED_CSV_DIR):
            if not csv_file.endswith(".csv"):
                continue
            
            input_csv_path = os.path.join(EXTRACTED_CSV_DIR, csv_file)

            with open(input_csv_path, mode="r", encoding="utf-8") as infile:
                reader = csv.reader(infile)
                next(reader, None)

                for row in reader:
                    if len(row) >= 2:
                        row[1] = mask_function_names(row[1])
                    writer.writerow(row)

            print(f"✅ Processed: {csv_file}")

process_csv_files()

print(f"\n🎉 All function names masked! Merged data saved in '{MASKED_CSV_PATH}'.")