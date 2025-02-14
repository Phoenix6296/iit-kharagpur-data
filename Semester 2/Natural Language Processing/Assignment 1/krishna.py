import pandas as pd
import re
import numpy as np
import math
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import defaultdict, Counter

class TextPreprocessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def remove_punct_and_non_ascii(self, text):
        text = re.sub(r'[^\w\s]', '', text)
        return text.encode('ascii', 'ignore').decode('ascii')

    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r'\d+', '<NUM>', text)
        return text

    def tokenize(self, text):
        return word_tokenize(text)

    def remove_stopwords(self, tokens):
        return [t for t in tokens if t not in self.stop_words]

    def lemmatize_tokens(self, tokens):
        return [self.lemmatizer.lemmatize(t) for t in tokens]

    def preprocess_pipeline(self, text):
        text = self.remove_punct_and_non_ascii(text)
        text = self.preprocess_text(text)
        tokens = self.tokenize(text)
        tokens = self.remove_stopwords(tokens)
        tokens = self.lemmatize_tokens(tokens)
        return tokens

class NGramModel:
    def __init__(self, train_df, test_df, min_freq=0.01, smoothing=1):
        self.train_df = train_df
        self.test_df = test_df
        self.min_freq = min_freq
        self.k = smoothing
        self.preprocessor = TextPreprocessor()

        self.train_tokens = self.preprocess_all(train_df)
        self.test_tokens = self.preprocess_all(test_df)

        self.unigram_vocab = self.build_vocab(self.train_tokens)
        self.train_tokens = [self.replace_oov(t) for t in self.train_tokens]
        self.test_tokens = [self.replace_oov(t) for t in self.test_tokens]

        self.unigram_probs = self.compute_unigram_probs()
        self.bigram_probs = self.compute_bigram_probs()
        self.trigram_probs = self.compute_trigram_probs()

    def preprocess_all(self, df):
        return [self.preprocessor.preprocess_pipeline(text) for text in df['text']]

    def build_vocab(self, tokens_list):
        min_count = max(1, int(len(tokens_list) * self.min_freq))
        article_counts = Counter(token for tokens in tokens_list for token in set(tokens))
        return {token for token, cnt in article_counts.items() if cnt >= min_count}

    def replace_oov(self, tokens):
        return [t if t in self.unigram_vocab else '<UNK>' for t in tokens]

    def compute_unigram_probs(self):
        unigram_counts = Counter(token for tokens in self.train_tokens for token in tokens)
        N = sum(unigram_counts.values())
        V = len(self.unigram_vocab)
        return {token: (unigram_counts[token] + self.k) / (N + self.k * V) for token in self.unigram_vocab}

    def compute_bigram_probs(self):
        bigram_counts = Counter((tokens[i], tokens[i+1]) for tokens in self.train_tokens for i in range(len(tokens)-1))
        unigram_counts = Counter(token for tokens in self.train_tokens for token in tokens)
        V = len(self.unigram_vocab)
        return {(w1, w2): (bigram_counts[(w1, w2)] + self.k) / (unigram_counts.get(w1, 0) + self.k * V)
                for (w1, w2) in bigram_counts}

    def compute_trigram_probs(self):
        trigram_counts = Counter((tokens[i], tokens[i+1], tokens[i+2]) for tokens in self.train_tokens for i in range(len(tokens)-2))
        bigram_counts = Counter((tokens[i], tokens[i+1]) for tokens in self.train_tokens for i in range(len(tokens)-1))
        V = len(self.unigram_vocab)
        return {(w1, w2, w3): (trigram_counts[(w1, w2, w3)] + self.k) / (bigram_counts.get((w1, w2), 0) + self.k * V)
                for (w1, w2, w3) in trigram_counts}

    def calculate_perplexity(self, tokens, model_type):
        log_sum = 0
        T = len(tokens)
        if model_type == 'unigram':
            for t in tokens:
                prob = self.unigram_probs.get(t, 1 / (sum(self.unigram_probs.values()) + len(self.unigram_vocab)))
                log_sum += math.log(prob)
        elif model_type == 'bigram':
            for i in range(1, T):
                bg = (tokens[i-1], tokens[i])
                prob = self.bigram_probs.get(bg, self.unigram_probs.get(tokens[i], 1 / len(self.unigram_vocab)))
                log_sum += math.log(prob)
        elif model_type == 'trigram':
            for i in range(2, T):
                tg = (tokens[i-2], tokens[i-1], tokens[i])
                prob = self.trigram_probs.get(tg, self.bigram_probs.get((tokens[i-1], tokens[i]), self.unigram_probs.get(tokens[i], 1 / len(self.unigram_vocab))))
                log_sum += math.log(prob)
        else:
            raise ValueError("Invalid model type")
        return math.exp(-log_sum / T) if T > 0 else float('inf')

    def evaluate_perplexity(self, model_type):
        perplexities = [self.calculate_perplexity(tokens, model_type) for tokens in self.test_tokens]
        return np.mean(perplexities)

    def interpolate_probs(self, tokens, lambdas):
        l1, l2, l3 = lambdas
        total_log = 0
        for i in range(len(tokens)):
            uni_prob = self.unigram_probs.get(tokens[i], 1 / len(self.unigram_vocab))
            bg_prob = self.bigram_probs.get((tokens[i-1], tokens[i]), uni_prob) if i > 0 else uni_prob
            tg_prob = self.trigram_probs.get((tokens[i-2], tokens[i-1], tokens[i]), bg_prob) if i > 1 else bg_prob
            prob = l1 * tg_prob + l2 * bg_prob + l3 * uni_prob
            total_log += math.log(prob)
        return math.exp(-total_log / len(tokens))

    def tune_interpolation(self, validation_tokens):
        best_ppl = float('inf')
        best_lambdas = (0.4, 0.3, 0.3)
        for l1 in np.linspace(0, 1, 11):
            for l2 in np.linspace(0, 1 - l1, 11):
                l3 = 1 - l1 - l2
                if l3 < 0:
                    continue
                avg_ppl = np.mean([self.interpolate_probs(t, (l1, l2, l3)) for t in validation_tokens])
                if avg_ppl < best_ppl:
                    best_ppl = avg_ppl
                    best_lambdas = (l1, l2, l3)
        return best_lambdas, best_ppl

# Load data
train_df = pd.read_csv('data/train.csv')
test_df = pd.read_csv('data/test.csv')

# Initialize and train the model
ngram_model = NGramModel(train_df, test_df)

# Evaluate perplexities
uni_ppl = ngram_model.evaluate_perplexity('unigram')
bi_ppl = ngram_model.evaluate_perplexity('bigram')
tri_ppl = ngram_model.evaluate_perplexity('trigram')

print(f"Unigram Perplexity: {uni_ppl}")
print(f"Bigram Perplexity: {bi_ppl}")
print(f"Trigram Perplexity: {tri_ppl}")

# Tune interpolation
validation_df = train_df.sample(n=100, random_state=42)
validation_tokens = ngram_model.preprocess_all(validation_df)

best_lambdas, interp_ppl = ngram_model.tune_interpolation(validation_tokens)
print(f"Best Lambdas: {best_lambdas}")
print(f"Interpolated Perplexity: {interp_ppl}")
