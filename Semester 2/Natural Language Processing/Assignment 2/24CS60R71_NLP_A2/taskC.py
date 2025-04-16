# Install required dependencies.
import os
import time
from typing import Any, Dict, List, Tuple

import pandas as pd
import torch
import transformers
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
)

# Install required dependencies.
# !pip install rouge_score datasets evaluate

from datasets import Dataset
import evaluate
from tqdm.auto import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set device for model training/inference.
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set style for plots
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

# Plot timing data
def plot_timing(timing_data: Dict[str, float], title: str = "Execution Time by Step"):
    plt.figure(figsize=(10, 6))
    colors = sns.color_palette("husl", len(timing_data))
    bars = plt.bar(timing_data.keys(), timing_data.values(), color=colors)

    plt.title(title, fontsize=14, pad=20)
    plt.ylabel("Time (seconds)", fontsize=12)
    plt.xticks(rotation=45, ha='right')

    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.1f}',
                 ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

# ROUGE Score Plotter
def plot_rouge_scores(rouge_data: Dict[str, Dict[str, float]],
                     model_name: str,
                     strategies: List[str]):
    metrics = ['rouge1', 'rouge2', 'rougeL']
    x = np.arange(len(metrics))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, strategy in enumerate(strategies):
        scores = [rouge_data[strategy][m] for m in metrics]
        offset = width * i
        rects = ax.bar(x + offset, scores, width, label=strategy)
        ax.bar_label(rects, padding=3, fmt='%.3f')

    ax.set_title(f'ROUGE Scores for {model_name}', fontsize=14, pad=20)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_xticks(x + width/2)
    ax.set_xticklabels(['ROUGE-1', 'ROUGE-2', 'ROUGE-L'])
    ax.legend(loc='upper right')
    ax.set_ylim(0, 1)

    fig.tight_layout()
    plt.show()

# Rouge Table Printer
def print_rouge_table(rouge_data: Dict[str, Dict[str, float]], title: str):
    print(f"\n{title}")
    print("-" * 60)
    print("{:<15} {:<15} {:<15} {:<15}".format(
        "Strategy", "ROUGE-1", "ROUGE-2", "ROUGE-L"))
    print("-" * 60)

    for strategy, scores in rouge_data.items():
        print("{:<15} {:<15.4f} {:<15.4f} {:<15.4f}".format(
            strategy,
            scores['rouge1'],
            scores['rouge2'],
            scores['rougeL']))
    print("-" * 60)

# Data Loading
def load_data(train_path: str, test_path: str, val_size: int = 500) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    start_time = time.time()
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        print("Train or test CSV file does not exist. Check the provided paths.")
        raise FileNotFoundError("Train or test CSV file not found.")

    train_df = pd.read_csv(train_path)
    val_df = train_df.sample(n=val_size, random_state=42)
    test_df = pd.read_csv(test_path)

    elapsed = time.time() - start_time
    print(f"Data loaded in {elapsed:.2f} seconds: Train shape = {train_df.shape}, Val shape = {val_df.shape}, Test shape = {test_df.shape}")
    return train_df, val_df, test_df

# Preprocessing
def preprocess(examples: Dict[str, Any],
               tokenizer: transformers.PreTrainedTokenizer,
               max_input_length: int = 512,
               max_target_length: int = 128) -> Dict[str, Any]:
    inputs = examples["text"]
    targets = examples["title"]
    tokenized_inputs = tokenizer(
        inputs,
        max_length=max_input_length,
        truncation=True,
        padding="max_length"
    )
    with tokenizer.as_target_tokenizer():
        tokenized_targets = tokenizer(
            targets,
            max_length=max_target_length,
            truncation=True,
            padding="max_length"
        )
    tokenized_inputs["labels"] = tokenized_targets["input_ids"]
    return tokenized_inputs

# T5 Title Generator
def generate_titles_t5(model: transformers.PreTrainedModel,
                       tokenizer: transformers.PreTrainedTokenizer,
                       test_df: pd.DataFrame,
                       beam_search: bool = False,
                       max_new_tokens: int = 40) -> List[str]:
    predictions = []
    for _, row in tqdm(test_df.iterrows(), total=len(test_df), desc="Generating titles"):
        inputs = tokenizer(
            row["text"],
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).to(device)

        outputs = model.generate(
            inputs["input_ids"],
            max_new_tokens=max_new_tokens,
            num_beams=4 if beam_search else 1,
            early_stopping=True
        )
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        predictions.append(decoded)
    return predictions

# Flan Title Generator
def generate_titles_flan(model: transformers.PreTrainedModel,
                         tokenizer: transformers.PreTrainedTokenizer,
                         test_df: pd.DataFrame,
                         prompt_template: str,
                         beam_search: bool = False,
                         max_new_tokens: int = 40) -> List[str]:
    predictions = []
    for _, row in tqdm(test_df.iterrows(), total=len(test_df), desc="Generating Flan titles"):
        prompted_text = prompt_template.format(row["text"])
        inputs = tokenizer(
            prompted_text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).to(device)

        outputs = model.generate(
            inputs["input_ids"],
            max_new_tokens=max_new_tokens,
            num_beams=4 if beam_search else 1,
            early_stopping=True
        )
        decoded_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        predictions.append(decoded_text)
    return predictions

# Evaluate Flan models with different prompts
def evaluate_prompts_flan(model_name: str,
                          test_df: pd.DataFrame,
                          prompts: Dict[str, str]) -> Dict[str, Any]:
    print(f"\nEvaluating {model_name} ...")
    start_time = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    print(f"Model loading took {time.time() - start_time:.2f} seconds")

    rouge = evaluate.load("rouge")
    results = {}

    for prompt_name, prompt_template in prompts.items():
        print(f"\nEvaluating prompt: '{prompt_name}'")

        # Greedy decoding
        greedy_start = time.time()
        greedy_preds = generate_titles_flan(model, tokenizer, test_df, prompt_template, beam_search=False)
        greedy_time = time.time() - greedy_start
        greedy_scores = rouge.compute(predictions=greedy_preds, references=test_df["title"].tolist())
        print("Sample generated titles (Greedy):")
        for title in greedy_preds[:3]:
            print(f"- {title}")

        # Beam search decoding
        beam_start = time.time()
        beam_preds = generate_titles_flan(model, tokenizer, test_df, prompt_template, beam_search=True)
        beam_time = time.time() - beam_start
        beam_scores = rouge.compute(predictions=beam_preds, references=test_df["title"].tolist())
        print("Sample generated titles (Beam):")
        for title in beam_preds[:3]:
            print(f"- {title}")

        results[prompt_name] = {
            "greedy": {
                "time": greedy_time,
                "rouge1": greedy_scores['rouge1'],
                "rouge2": greedy_scores['rouge2'],
                "rougeL": greedy_scores['rougeL']
            },
            "beam": {
                "time": beam_time,
                "rouge1": beam_scores['rouge1'],
                "rouge2": beam_scores['rouge2'],
                "rougeL": beam_scores['rougeL']
            }
        }

    print(f"\nEvaluation for {model_name} completed in {time.time() - start_time:.2f} seconds")
    return results

# Main function to orchestrate the workflow
def main():
    total_start_time = time.time()
    timing_data = {}

    # Define paths to the CSV files.
    train_csv_path = "/content/train.csv"
    test_csv_path = "/content/test.csv"

    # Step 1: Load the datasets.
    print("\n" + "="*50)
    print("Step 1: Loading data...")
    step1_start = time.time()
    train_df, val_df, test_df = load_data(train_csv_path, test_csv_path, val_size=500)
    timing_data["Data Loading"] = time.time() - step1_start

    # Step 2: Setup model and tokenizer
    print("\n" + "="*50)
    print("Step 2: Setting up model and tokenizing data...")
    step2_start = time.time()

    t5_model_name = "google-t5/t5-small"
    t5_tokenizer = AutoTokenizer.from_pretrained(t5_model_name)
    t5_model = AutoModelForSeq2SeqLM.from_pretrained(t5_model_name).to(device)

    train_dataset = Dataset.from_pandas(train_df)
    val_dataset = Dataset.from_pandas(val_df)

    tokenized_train = train_dataset.map(lambda x: preprocess(x, t5_tokenizer), batched=True)
    tokenized_val = val_dataset.map(lambda x: preprocess(x, t5_tokenizer), batched=True)

    timing_data["Model Setup"] = time.time() - step2_start

    # Step 3: Training
    print("\n" + "="*50)
    print("Step 3: Training the T5-small model...")
    step3_start = time.time()

    training_args = Seq2SeqTrainingArguments(
        output_dir="./t5_results",
        evaluation_strategy="epoch",
        logging_strategy="epoch",
        run_name="transformer",
        learning_rate=3e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        save_total_limit=3,
        predict_with_generate=True,
        fp16=True if device.type == "cuda" else False,
        report_to=[],
    )

    trainer = Seq2SeqTrainer(
        model=t5_model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        tokenizer=t5_tokenizer,
    )

    trainer.train()
    timing_data["Training"] = time.time() - step3_start

    # Step 4: Evaluation - T5-small decoding strategies.
    print("\n" + "="*50)
    print("Step 4: Evaluating T5-small with decoding strategies...")
    step4_start = time.time()

    rouge_metric = evaluate.load("rouge")
    t5_results = {}

    for strategy, beam in [("Greedy", False), ("Beam Search", True)]:
        print(f"\nRunning {strategy} decoding...")
        predictions = generate_titles_t5(t5_model, t5_tokenizer, test_df, beam_search=beam)

        # Print sample generated titles
        print(f"\nSample generated titles ({strategy} decoding):")
        for i in range(3):  # Print first 3 examples
            print(f"Original: {test_df['title'].iloc[i]}")
            print(f"Generated: {predictions[i]}")
            print("-" * 50)

        scores = rouge_metric.compute(predictions=predictions, references=test_df["title"].tolist())
        t5_results[strategy] = {
            "rouge1": scores['rouge1'],
            "rouge2": scores['rouge2'],
            "rougeL": scores['rougeL']
        }

    timing_data["T5 Evaluation"] = time.time() - step4_start

    # Step 5: Evaluate Flan models with various prompts.
    print("\n" + "="*50)
    print("Step 5: Evaluating Flan models with various prompts...")
    step5_start = time.time()

    prompts = {
        "Basic": "Generate a title for: {}",
        "Detailed": "Create a concise title for this Wikipedia article: {}",
    }

    flan_results = {}
    for model_size in ["base", "large"]:
        model_name = f"google/flan-t5-{model_size}"
        results = evaluate_prompts_flan(model_name, test_df, prompts)
        flan_results[model_name] = results

    timing_data["Flan Evaluation"] = time.time() - step5_start

    # Final summary
    print("\n" + "="*50)
    print("All evaluation steps completed.")
    timing_data["Total Time"] = time.time() - total_start_time

    # Visualization
    print("\n" + "="*50)
    print("Visualizing Results...")

    # Plot timing data
    plot_timing(timing_data, "Execution Time by Step")

    # Print and plot T5 results
    print_rouge_table(t5_results, "Finetuned T5-small Performance")
    plot_rouge_scores(t5_results, "Finetuned T5-small", ["Greedy", "Beam Search"])

    # Print and plot Flan results
    for model_name, results in flan_results.items():
        # Combine results for both prompts
        combined_results = {
            f"Greedy ({prompt})": res["greedy"]
            for prompt, res in results.items()
        }
        combined_results.update({
            f"Beam ({prompt})": res["beam"]
            for prompt, res in results.items()
        })

        # Extract just the ROUGE scores
        rouge_scores = {
            strategy: {k: v for k, v in scores.items() if k.startswith('rouge')}
            for strategy, scores in combined_results.items()
        }

        print_rouge_table(rouge_scores, f"{model_name} Performance")

        # Plot for each prompt type
        for prompt in prompts.keys():
            prompt_results = {
                "Greedy": results[prompt]["greedy"],
                "Beam": results[prompt]["beam"]
            }
            plot_rouge_scores(prompt_results, f"{model_name} - {prompt} Prompt", ["Greedy", "Beam"])

if __name__ == "__main__":
    main()