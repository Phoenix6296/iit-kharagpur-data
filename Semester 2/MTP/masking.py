import os
import csv
import libcst as cst
import ollama

BASE_DIR = os.getcwd()
EXTRACTED_CSV_DIR = os.path.join(BASE_DIR, "Extracted_CSV")
HYBRID_CSV_DIR = os.path.join(BASE_DIR, "Hybrid_CSV")

# Ensure Hybrid_CSV directory exists
os.makedirs(HYBRID_CSV_DIR, exist_ok=True)

# Custom transformer to extract function names
class FunctionExtractor(cst.CSTVisitor):
    def __init__(self):
        self.functions = []

    def visit_FunctionDef(self, node):
        self.functions.append(node.name.value)

# Transformer to mask function definitions and calls
class FunctionMasker(cst.CSTTransformer):
    def __init__(self, target_function):
        self.target_function = target_function

    def leave_FunctionDef(self, original_node, updated_node):
        if original_node.name.value == self.target_function:
            print(f"🔹 Masking function definition: {original_node.name.value}")  # Debugger
            return updated_node.with_changes(name=cst.Name(value="MASKED_FUNCTION"))

        return updated_node

    def leave_Call(self, original_node, updated_node):
        if isinstance(original_node.func, cst.Name) and original_node.func.value == self.target_function:
            print(f"🔹 Masking function call: {original_node.func.value}")  # Debugger
            return updated_node.with_changes(func=cst.Name(value="MASKED_FUNCTION"))

        return updated_node

# Extracts function names from Python code
def extract_functions(code):
    print("\n🔍 Extracting functions...")
    tree = cst.parse_module(code)
    extractor = FunctionExtractor()
    tree.visit(extractor)
    if extractor.functions == []:
        print("❌ No functions found.")
    else:
        print(f"📌 Found functions: {extractor.functions}")  # Debugger
    return extractor.functions

# Masks a specific function name and its calls in the code
def mask_function(code, function_name):
    print(f"✏️  Masking function and its calls: {function_name}")
    tree = cst.parse_module(code)
    masker = FunctionMasker(function_name)
    new_tree = tree.visit(masker)
    masked_code = new_tree.code
    # print(f"🔎 Masked Code:\n{masked_code}")
    return masked_code

# Uses Ollama to predict the function name
def predict_function_name(masked_code):
    print(f"\n🤖 Predicting function name for masked code...")
    prompt = f"{masked_code}\n\nPredict the MASKED_FUNCTION name. In answer only give the function name."
    try:
        response = ollama.chat(model="deepseek-r1", messages=[{"role": "user", "content": prompt}])
        predicted_name = response["message"]["content"].strip()
        print(f"✅ Predicted Name: {predicted_name}")  # Debugger
        return predicted_name
    except Exception as e:
        print(f"❌ Error in Ollama prediction: {e}")
        return "UNKNOWN_FUNCTION"

# Replaces masked function name with predicted name
def replace_function_name(code, old_name, new_name):
    print(f"🔄 Replacing {old_name} with {new_name}")
    return code.replace(f"MASKED_FUNCTION", new_name)

# Processes all CSV files
def process_csv_files():
    print(f"\n📂 Processing files in: {EXTRACTED_CSV_DIR}\n")
    for csv_file in os.listdir(EXTRACTED_CSV_DIR):
        if not csv_file.endswith(".csv"):
            continue

        extracted_csv_path = os.path.join(EXTRACTED_CSV_DIR, csv_file)
        hybrid_csv_path = os.path.join(HYBRID_CSV_DIR, f"hybrid_{csv_file}")

        print(f"\n🚀 Processing file: {csv_file}")  # Debugger
        with open(extracted_csv_path, "r", encoding="utf-8") as infile, \
             open(hybrid_csv_path, "w", newline="", encoding="utf-8") as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            writer.writerow(["Filename", "Modified Code"])

            next(reader)  # Skip header

            for row in reader:
                filename, code = row
                print(f"\n📜 Processing script: {filename}")

                functions = extract_functions(code)

                for func_name in functions:
                    print(f"\n🔄 Picking function: {func_name}")
                    masked_code = mask_function(code, func_name)
                    predicted_name = predict_function_name(masked_code)
                    code = replace_function_name(code, func_name, predicted_name)

                writer.writerow([filename, code])
                print(f"✅ Modified script saved for {filename}")  # Debugger

        print(f"\n✅ Processed {csv_file} -> {hybrid_csv_path}")

process_csv_files()
print("\n🎉 All CSVs processed! Modified CSVs are in 'Hybrid_CSV' folder.")