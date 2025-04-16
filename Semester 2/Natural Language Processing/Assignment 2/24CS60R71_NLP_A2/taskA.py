# Import Libraries
import spacy
import pandas as pd
import re
import string
from tqdm import tqdm
import time

spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])

train_df = pd.read_csv('/kaggle/input/nlp-a2-dataset/train.csv')
test_df = pd.read_csv('/kaggle/input/nlp-a2-dataset/test.csv')

print(f"Training set size: {len(train_df)}")
print(f"Test set size: {len(test_df)}")
print("\nSample raw training data:")
print(train_df.head(2))

# Preprocess Text Data
tqdm.pandas()

def preprocess_text(text):
    text = text.lower().encode('ascii', errors='ignore').decode('utf-8')
    text = text.translate(str.maketrans('', '', string.punctuation))

    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    return " ".join(tokens)


start = time.time()

# Process training data
print("Processing training data...")
train_df['processed_text'] = train_df['text'].progress_apply(preprocess_text)

# Process test data
print("\nProcessing test data...")
test_df['processed_text'] = test_df['text'].progress_apply(preprocess_text)

print("\nTotal time taken in preprocessing: ", time.time() - start)

# Create validation set
validation_df = train_df.iloc[:500].copy()
train_df = train_df.iloc[500:].reset_index(drop=True)

# Summary
print("\nDataset shape after preprocessing:")
print(f"Training set size: {len(train_df)}")
print(f"Validation set size: {len(validation_df)}")
print(f"Test set size: {len(test_df)}")

print("\nSample processed data:")
print(train_df[['title', 'processed_text']].head(2))