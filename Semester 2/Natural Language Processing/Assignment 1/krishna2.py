import pandas as pd
import re
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import defaultdict, Counter
import math


#TRAINING DATA
train_df = pd.read_csv('data/train.csv')
test_df = pd.read_csv('data/test.csv')

validation_df = train_df.sample(n=100, random_state=42)
new_train_df = train_df.drop(validation_df.index)


#PREPROCESSING
def preprocess_all(df):
    df['text'] = df['text'].apply(lambda x: x.encode("ascii", "ignore").decode())
    df['text'] = df['text'].apply(lambda x: re.sub(r'[^\w\s]', '', x))
    df['text'] = df['text'].apply(lambda x: x.lower())
    df['text'] = df['text'].apply(lambda x: re.sub(r'\d+', '<NUM>', x))
    df['text'] = df['text'].apply(lambda x: word_tokenize(x))
    stop_words = set(stopwords.words('english'))
    df['text'] = df['text'].apply(lambda x: [word for word in x if word not in stop_words])
    lemmatizer = WordNetLemmatizer()
    df['text'] = df['text'].apply(lambda x: [lemmatizer.lemmatize(word) for word in x])
    return df['text']

new_train_tokens = preprocess_all(new_train_df)
validation_tokens = preprocess_all(validation_df)
test_tokens = preprocess_all(test_df)


#VOCABULARY BUILDING
def compute_min_count(dataset_size, threshold=0.01):
    """Compute the minimum count threshold for vocabulary inclusion."""
    return max(1, int(dataset_size * threshold))

def build_unigram_vocab(tokenized_texts, min_count):
    """Build unigram vocabulary based on article frequency count."""
    article_counts = defaultdict(int)
    
    for tokens in tokenized_texts:
        for token in set(tokens):  # Consider only unique tokens per document
            article_counts[token] += 1
    
    return {token for token, count in article_counts.items() if count >= min_count}

def replace_oov(tokens, vocab):
    """Replace out-of-vocabulary (OOV) tokens with '<UNK>'."""
    return [token if token in vocab else '<UNK>' for token in tokens]

def build_ngram_vocab(tokenized_texts, n, min_count):
    """Build an n-gram vocabulary with a given minimum count threshold."""
    article_counts = defaultdict(int)

    for tokens in tokenized_texts:
        ngrams = set(zip(*[tokens[i:] for i in range(n)]))  # Extract unique n-grams
        for ngram in ngrams:
            article_counts[ngram] += 1

    return {ngram for ngram, count in article_counts.items() if count >= min_count}

# Compute min_count based on dataset size
min_count = compute_min_count(len(new_train_df))

# Build Unigram Vocabulary
unigram_vocab = build_unigram_vocab(new_train_tokens, min_count)

# Replace OOV words in train, validation, and test datasets
new_train_tokens = [replace_oov(tokens, unigram_vocab) for tokens in new_train_tokens]
validation_tokens = [replace_oov(tokens, unigram_vocab) for tokens in validation_tokens]
test_tokens = [replace_oov(tokens, unigram_vocab) for tokens in test_tokens]

# Build Bigram and Trigram Vocabularies
bigram_vocab = build_ngram_vocab(new_train_tokens, n=2, min_count=min_count)
trigram_vocab = build_ngram_vocab(new_train_tokens, n=3, min_count=min_count)


#COMPUTING MAXIMUM LIKELIHOOD ESTIMATES
def compute_unigram_probs(new_train_tokens, unigram_vocab, k=1):
    """Compute unigram probabilities with Laplace smoothing."""
    unigram_counts = Counter()
    
    for tokens in new_train_tokens:
        unigram_counts.update(tokens)
    
    N_uni = sum(unigram_counts.values())
    V = len(unigram_vocab)
    
    unigram_probs = {
        token: (unigram_counts[token] + k) / (N_uni + k * V)
        for token in unigram_vocab
    }
    
    return unigram_probs, unigram_counts, N_uni, V

def compute_ngram_probs(new_train_tokens, n, ngram_vocab, unigram_counts=None, k=1):
    ngram_counts = Counter()
    context_counts = Counter()
    
    for tokens in new_train_tokens:
        ngrams = list(zip(*[tokens[i:] for i in range(n)]))
        ngram_counts.update(ngrams)
        
        if n > 1:
            contexts = list(zip(*[tokens[i:] for i in range(n - 1)]))
            context_counts.update(contexts)

    V = len(ngram_vocab)
    ngram_probs = {}

    for ngram in ngram_vocab:
        context = ngram[:-1]
        count_ngram = ngram_counts[ngram]
        count_context = context_counts.get(context, 0) if n > 1 else unigram_counts.get(ngram[0], 0)

        ngram_probs[ngram] = (count_ngram + k) / (count_context + k * V)

    return ngram_probs, ngram_counts, context_counts, V

# Compute Unigram Probabilities
unigram_probs, unigram_counts, N_uni, V = compute_unigram_probs(new_train_tokens, unigram_vocab, k=1)

# Compute Bigram Probabilities
bigram_probs, bigram_counts, _, V = compute_ngram_probs(new_train_tokens, 2, bigram_vocab, unigram_counts, k=1)

# Compute Trigram Probabilities
trigram_probs, trigram_counts, bigram_context_counts, V = compute_ngram_probs(new_train_tokens, 3, trigram_vocab, k=1)


# PERPLEXITY CALCULATION
def compute_perplexity(test_tokens, model_type, ngram_probs, context_counts, V):
    perplexities = []

    for tokens in test_tokens:
        log_sum = 0
        T = len(tokens)

        if model_type == 'unigram':
            for t in tokens:
                prob = ngram_probs.get(t, 1 / (N_uni + V))
                log_sum += math.log(prob)

        elif model_type == 'bigram':
            T -= 1  # Adjust for bigram count
            for i in range(1, len(tokens)):
                bg = (tokens[i-1], tokens[i])
                prob = ngram_probs.get(bg, 1 / (unigram_counts.get(tokens[i-1], 0) + V))
                log_sum += math.log(prob)

        elif model_type == 'trigram':
            T -= 2  # Adjust for trigram count
            for i in range(2, len(tokens)):
                tg = (tokens[i-2], tokens[i-1], tokens[i])
                prob = ngram_probs.get(tg, 1 / (context_counts.get((tokens[i-2], tokens[i-1]), 0) + V))
                log_sum += math.log(prob)

        else:
            raise ValueError("Invalid model type")

        perplexity = math.exp(-log_sum / T) if T > 0 else float('inf')
        perplexities.append(perplexity)

    return np.mean(perplexities)

uni_ppl = compute_perplexity(test_tokens, 'unigram', unigram_probs, None, V)
bi_ppl = compute_perplexity(test_tokens, 'bigram', bigram_probs, unigram_counts, V)
tri_ppl = compute_perplexity(test_tokens, 'trigram', trigram_probs, bigram_context_counts, V)

# Print results
print(f"Unigram Perplexity: {uni_ppl}")
print(f"Bigram Perplexity: {bi_ppl}")
print(f"Trigram Perplexity: {tri_ppl}")


# Interpolation modelimport math
def interpolated_prob(tokens, lambdas, unigram_probs, bigram_probs, trigram_probs, N_uni, V):
    l1, l2, l3 = lambdas
    total_log = 0

    for i in range(len(tokens)):
        uni_prob = unigram_probs.get(tokens[i], 1 / (N_uni + V))
        bi_prob = bigram_probs.get((tokens[i-1], tokens[i]), uni_prob) if i > 0 else uni_prob
        tri_prob = trigram_probs.get((tokens[i-2], tokens[i-1], tokens[i]), bi_prob) if i > 1 else bi_prob

        prob = l1 * tri_prob + l2 * bi_prob + l3 * uni_prob
        total_log += math.log(prob)

    return math.exp(-total_log / len(tokens))

def optimize_interpolation(validation_tokens, unigram_probs, bigram_probs, trigram_probs, N_uni, V):
    best_ppl = float('inf')
    best_lambdas = (0.4, 0.3, 0.3)

    for l1 in np.linspace(0, 1, 11):
        for l2 in np.linspace(0, 1 - l1, 11):
            l3 = 1 - l1 - l2
            if l3 < 0:
                continue

            avg_ppl = np.mean([
                interpolated_prob(tokens, (l1, l2, l3), unigram_probs, bigram_probs, trigram_probs, N_uni, V) 
                for tokens in validation_tokens
            ])

            if avg_ppl < best_ppl:
                best_ppl = avg_ppl
                best_lambdas = (l1, l2, l3)

    return best_lambdas, best_ppl

# Optimize interpolation
best_lambdas, best_ppl = optimize_interpolation(validation_tokens, unigram_probs, bigram_probs, trigram_probs, N_uni, V)

# Evaluate on test data
interp_ppl = np.mean([
    interpolated_prob(tokens, best_lambdas, unigram_probs, bigram_probs, trigram_probs, N_uni, V) 
    for tokens in test_tokens
])

# Print results
print(f"Best Lambdas: {best_lambdas}")
print(f"Interpolated Perplexity: {interp_ppl}")
