import os
import csv
import ast
import ollama

BASE_DIR = os.getcwd()
EXTRACTED_CSV_DIR = os.path.join(BASE_DIR, "Extracted_CSV")
HYBRID_CSV_DIR = os.path.join(BASE_DIR, "Hybrid_CSV")

# Ensure Hybrid_CSV directory exists
os.makedirs(HYBRID_CSV_DIR, exist_ok=True)

def extract_functions(code):
    """Extracts functions from the given Python code and returns a list of (name, code, start, end)."""
    functions = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno - 1
                end_line = node.body[-1].lineno
                func_code = "\n".join(code.splitlines()[start_line:end_line])
                functions.append((node.name, func_code, start_line, end_line))
    except Exception as e:
        print(f"Error parsing code: {e}")
    return functions

def mask_function(code, start_line, end_line):
    """Replaces the function definition with a masked version."""
    lines = code.splitlines()
    masked_code = lines[:start_line] + ["def MASKED_FUNCTION(...):\n    pass"] + lines[end_line:]
    return "\n".join(masked_code)

def predict_function_name(masked_code):
    """Uses Ollama to predict the function name."""
    prompt = f"Given the following Python code with a masked function:\n\n{masked_code}\n\nPredict the function name:"
    try:
        response = ollama.chat(model="deepseek-r1", messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"].strip()
    except Exception as e:
        print(f"Error in Ollama prediction: {e}")
        return "UNKNOWN_FUNCTION"

def process_csv_files():
    """Processes all CSV files in Extracted_CSV."""
    for csv_file in os.listdir(EXTRACTED_CSV_DIR):
        if not csv_file.endswith(".csv"):
            continue

        extracted_csv_path = os.path.join(EXTRACTED_CSV_DIR, csv_file)
        hybrid_csv_path = os.path.join(HYBRID_CSV_DIR, f"hybrid_{csv_file}")

        with open(extracted_csv_path, "r", encoding="utf-8") as infile, \
             open(hybrid_csv_path, "w", newline="", encoding="utf-8") as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            writer.writerow(["Filename", "Modified Code"])

            next(reader)  # Skip header

            for row in reader:
                filename, code = row
                functions = extract_functions(code)

                for func_name, func_code, start, end in functions:
                    masked_code = mask_function(code, start, end)
                    predicted_name = predict_function_name(masked_code)
                    code = code.replace(f"def {func_name}", f"def {predicted_name}")

                writer.writerow([filename, code])

        print(f"✅ Processed {csv_file} -> {hybrid_csv_path}")

process_csv_files()
print("\n🎉 All CSVs processed! Modified CSVs are in 'Hybrid_CSV' folder.")
