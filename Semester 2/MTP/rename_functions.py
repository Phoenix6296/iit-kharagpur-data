import csv
import re
import ollama

MASKED_CSV = "masked_data.csv"
OUTPUT_CSV = "data_ai.csv"

# Regular expression to find one masked function at a time
FUNC_PATTERN = re.compile(r"(def MASKED_FUNCTION\(.*?\):(?:\n    .*)*)", re.DOTALL)

# Gets an explanation of the function from Ollama
def explain_function(function_code):
    prompt = f"""Explain the following function in detail
    ```python
    {function_code}
    ```
    """
    response = ollama.chat(model="deepseek-r1", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()

# Asks Ollama to regenerate the function based on its explanation
def regenerate_function(explanation):
    prompt = f"""Use the explanation to generate only the python function code.
    {explanation}
    Just give the code and nothing else.
    """
    response = ollama.chat(model="deepseek-r1", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()

# Processes the masked dataset, replacing one function at a time
def process_csv():
    with open(MASKED_CSV, "r", encoding="utf-8") as infile, open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Copy header
        header = next(reader)
        writer.writerow(header)

        for row in reader:
            filename, code = row
            print(f"\n🔍 Processing file: {filename}")  # Debugging

            updated_code = code

            while True:
                match = FUNC_PATTERN.search(updated_code)
                if not match:
                    break

                masked_function = match.group(1)
                print(f"🔹 Found masked function:\n{masked_function}\n")

                # Get explanation from Ollama
                explanation = explain_function(masked_function)
                print(f"📖 Ollama Explanation:\n{explanation}\n")

                # Generate the new function
                new_function = regenerate_function(explanation)
                print(f"💡 Generated Function:\n{new_function}\n")

                # Replace only the current function, then search for the next one
                updated_code = updated_code.replace(masked_function, new_function, 1)

            # Write the modified data
            writer.writerow([filename, updated_code])
            print(f"✅ Processed: {filename}")

# Run the function processing
process_csv()
print("\n🎉 Function names predicted and saved to 'data_ai.csv'.")
