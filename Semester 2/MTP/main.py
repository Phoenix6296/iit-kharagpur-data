import os
import csv
import shutil
import subprocess

BASE_DIR = os.getcwd()
EXTRACTED_CSV_DIR = os.path.join(BASE_DIR, "Extracted_CSV")
REPO_LIST_FILE = os.path.join(BASE_DIR, "repos.txt")

# Ensure the extracted CSV folder exists
os.makedirs(EXTRACTED_CSV_DIR, exist_ok=True)

# Reads repository URLs from a text file
def read_repo_list(file_path):
    if not os.path.exists(file_path):
        print(f"⚠️ File {file_path} not found! Please create 'repos.txt' with GitHub URLs.")
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        repos = [line.strip() for line in f if line.strip()]
    
    return repos

# Extracts the repository name from the GitHub URL
def get_repo_name(repo_url):
    return repo_url.rstrip(".git").split("/")[-1]

# Clones the GitHub repository into a directory
def clone_repo(repo_url, repo_name):
    clone_path = os.path.join(BASE_DIR, repo_name)
    
    if os.path.exists(clone_path):
        shutil.rmtree(clone_path)

    print(f"📥 Cloning {repo_url} into {clone_path}...")
    subprocess.run(["git", "clone", repo_url, clone_path], check=True)
    
    return clone_path

# Finds all Python files in the repository
def extract_python_files(repo_path):
    python_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

# Saves extracted Python files into a CSV file inside Extracted_CSV folder
def save_to_csv(repo_name, python_files):
    output_csv = os.path.join(EXTRACTED_CSV_DIR, f"{repo_name}.csv")
    
    with open(output_csv, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Filename", "Code"])

        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                    writer.writerow([file_path.replace(BASE_DIR + "/", ""), code])
            except Exception as e:
                print(f"⚠️ Skipping {file_path}: {e}")

    print(f"✅ Extracted {len(python_files)} Python files into {output_csv}")
    return output_csv

# Deletes the cloned repository after processing
def delete_repo(repo_path):
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)
        print(f"🗑️ Deleted repository: {repo_path}")

# Processes each repository: clone, extract, save, and delete
def process_repositories(repo_list):
    for repo_url in repo_list:
        repo_name = get_repo_name(repo_url)
        output_csv = os.path.join(EXTRACTED_CSV_DIR, f"{repo_name}.csv")
        
        if os.path.exists(output_csv):
            print(f"⏭️ Skipping {repo_name}: CSV already exists.")
            continue
        
        repo_path = clone_repo(repo_url, repo_name)
        python_files = extract_python_files(repo_path)
        save_to_csv(repo_name, python_files)
        delete_repo(repo_path)

# Read repositories from text file and process them
repo_urls = read_repo_list(REPO_LIST_FILE)
if repo_urls:
    process_repositories(repo_urls)
    print("\n🎉 All repositories processed! Extracted CSVs are in 'Extracted_CSV' folder.")
else:
    print("⚠️ No repositories found in repos.txt. Exiting.")
