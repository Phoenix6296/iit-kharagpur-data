import os
import csv
import shutil
import subprocess

# Set repository details
GITHUB_REPO_URL = "https://github.com/public-apis/public-apis.git"  # Change this to your repo
CLONE_DIR = "repo_clone"
OUTPUT_CSV = "python_code.csv"

# Clone the repository
if os.path.exists(CLONE_DIR):
    shutil.rmtree(CLONE_DIR)  # Remove existing repo folder
subprocess.run(["git", "clone", GITHUB_REPO_URL, CLONE_DIR], check=True)

# Collect all Python files
python_files = []
for root, _, files in os.walk(CLONE_DIR):
    for file in files:
        if file.endswith(".py"):
            python_files.append(os.path.join(root, file))

# Write to CSV
with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Filename", "Code"])  # CSV Header

    for file_path in python_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
                writer.writerow([file_path, code])
        except Exception as e:
            print(f"Skipping {file_path}: {e}")

print(f"Extracted Python code from {len(python_files)} files into {OUTPUT_CSV}")
