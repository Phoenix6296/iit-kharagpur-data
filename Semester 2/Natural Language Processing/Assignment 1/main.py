import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import defaultdict, Counter
import numpy as np
import re
import math
import time


class NgramLanguageModel:
    def __init__(self, train_path, test_path):
        # Reading training and test data
        self.train_df = pd.read_csv(train_path)
        self.test_df = pd.read_csv(test_path)

        # Splitting validation and training data
        self.validation_df = self.train_df.sample(n=100, random_state=71)
        self.new_train_df = self.train_df.drop(self.validation_df.index)

        # Preprocessing
        preprocessing_start_time = time.time()
        self.new_train_tokens = self.preprocess_all(self.new_train_df)
        self.validation_tokens = self.preprocess_all(self.validation_df)
        self.test_tokens = self.preprocess_all(self.test_df)
        preprocessing_end_time = time.time()
        print(f"Preprocessing Time: {(preprocessing_end_time - preprocessing_start_time):.2f} seconds")

        # Vocabulary Building
        self.min_count = self.compute_min_count(len(self.new_train_df))
        self.unigram_vocab = self.build_unigram_vocab(self.new_train_tokens, self.min_count)

        # Handling Out-of-Vocabulary Words
        self.new_train_tokens = [self.replace_oov(tokens, self.unigram_vocab) for tokens in self.new_train_tokens]
        self.validation_tokens = [self.replace_oov(tokens, self.unigram_vocab) for tokens in self.validation_tokens]
        self.test_tokens = [self.replace_oov(tokens, self.unigram_vocab) for tokens in self.test_tokens]

        # Building N-Gram Vocabulary
        self.bigram_vocab = self.build_ngram_vocab(self.new_train_tokens, n=2, min_count=self.min_count)
        self.trigram_vocab = self.build_ngram_vocab(self.new_train_tokens, n=3, min_count=self.min_count)

        # Computing Maximum Likelihood Estimates
        mle_start_time = time.time()
        self.unigram_probs, self.unigram_counts, self.N_uni, self.V = self.compute_unigram_probs(self.new_train_tokens)
        self.bigram_probs, self.bigram_counts, _, _ = self.compute_ngram_probs(self.new_train_tokens, 2, self.bigram_vocab, self.unigram_counts)
        self.trigram_probs, self.trigram_counts, self.bigram_context_counts, _ = self.compute_ngram_probs(self.new_train_tokens, 3, self.trigram_vocab)
        mle_end_time = time.time()
        print(f"MLE Time: {(mle_end_time - mle_start_time):.2f} seconds")

    # Preprocess a given text
    @staticmethod
    def preprocess_text(text):
        text = text.encode("ascii", "ignore").decode()
        text = re.sub(r'[^\w\s]', '', text).lower()
        text = re.sub(r'\d+', '<NUM>', text)
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(word) for word in tokens]

    # Preprocess the entire dataset
    def preprocess_all(self, df):
        return df['text'].apply(self.preprocess_text)

    # Compute the minimum count threshold for vocabulary inclusion
    @staticmethod
    def compute_min_count(dataset_size, threshold=0.01):
        return max(1, int(dataset_size * threshold))

    # Build unigram vocabulary based on frequency count
    @staticmethod
    def build_unigram_vocab(tokenized_texts, min_count):
        article_counts = defaultdict(int)
        for tokens in tokenized_texts:
            for token in set(tokens):
                article_counts[token] += 1
        return {token for token, count in article_counts.items() if count >= min_count}

    # Replace out-of-vocabulary (OOV) tokens with '<UNK>'
    @staticmethod
    def replace_oov(tokens, vocab):
        return [token if token in vocab else '<UNK>' for token in tokens]

    # Build an n-gram vocabulary with a given minimum count threshold
    @staticmethod
    def build_ngram_vocab(tokenized_texts, n, min_count):
        article_counts = defaultdict(int)
        for tokens in tokenized_texts:
            ngrams = set(zip(*[tokens[i:] for i in range(n)]))
            for ngram in ngrams:
                article_counts[ngram] += 1
        return {ngram for ngram, count in article_counts.items() if count >= min_count}

    # Compute unigram probabilities with Laplace smoothing
    def compute_unigram_probs(self, new_train_tokens, k=1):
        unigram_counts = Counter()
        for tokens in new_train_tokens:
            unigram_counts.update(tokens)
        N_uni = sum(unigram_counts.values())
        V = len(self.unigram_vocab)
        unigram_probs = {token: (unigram_counts[token] + k) / (N_uni + k * V) for token in self.unigram_vocab}
        return unigram_probs, unigram_counts, N_uni, V

    # Compute n-gram probabilities with Laplace smoothing
    def compute_ngram_probs(self, new_train_tokens, n, ngram_vocab, unigram_counts=None, k=1):
        ngram_counts = Counter()
        context_counts = Counter()
        for tokens in new_train_tokens:
            ngrams = list(zip(*[tokens[i:] for i in range(n)]))
            ngram_counts.update(ngrams)
            if n > 1:
                contexts = list(zip(*[tokens[i:] for i in range(n - 1)]))
                context_counts.update(contexts)

        V = len(ngram_vocab)
        ngram_probs = {
            ngram: (ngram_counts[ngram] + k) / (context_counts.get(ngram[:-1], 0) + k * V)
            for ngram in ngram_vocab
        }
        return ngram_probs, ngram_counts, context_counts, V

    # Compute perplexity for a given model type (unigram, bigram, trigram)
    def compute_perplexity(self, test_tokens, model_type, ngram_probs, context_counts):
        perplexities = []
        V = self.V

        for tokens in test_tokens:
            log_sum = 0
            T = len(tokens)

            if model_type == 'unigram':
                for t in tokens:
                    prob = ngram_probs.get(t, 1 / (self.N_uni + V))
                    log_sum += math.log(prob)
            elif model_type == 'bigram':
                T -= 1
                for i in range(1, len(tokens)):
                    prob = ngram_probs.get((tokens[i-1], tokens[i]), 1 / (self.unigram_counts.get(tokens[i-1], 0) + V))
                    log_sum += math.log(prob)
            elif model_type == 'trigram':
                T -= 2
                for i in range(2, len(tokens)):
                    prob = ngram_probs.get((tokens[i-2], tokens[i-1], tokens[i]), 1 / (context_counts.get((tokens[i-2], tokens[i-1]), 0) + V))
                    log_sum += math.log(prob)
            else:
                raise ValueError("Invalid model type")

            perplexities.append(math.exp(-log_sum / T) if T > 0 else float('inf'))

        return np.mean(perplexities)

    # Compute probability using interpolation model
    def interpolated_prob(self, tokens, lambdas):
        l1, l2, l3 = lambdas
        total_log = 0
        for i in range(len(tokens)):
            uni_prob = self.unigram_probs.get(tokens[i], 1 / (self.N_uni + self.V))
            bi_prob = self.bigram_probs.get((tokens[i-1], tokens[i]), uni_prob) if i > 0 else uni_prob
            tri_prob = self.trigram_probs.get((tokens[i-2], tokens[i-1], tokens[i]), bi_prob) if i > 1 else bi_prob
            prob = l1 * tri_prob + l2 * bi_prob + l3 * uni_prob
            total_log += math.log(prob)
        return math.exp(-total_log / len(tokens))

    # Optimize interpolation parameters using validation data
    def optimize_interpolation(self):
        best_ppl = float('inf')
        best_lambdas = (0.4, 0.3, 0.3)
        for l1 in np.linspace(0, 1, 11):
            for l2 in np.linspace(0, 1 - l1, 11):
                l3 = 1 - l1 - l2
                if l3 < 0:
                    continue
                avg_ppl = np.mean([self.interpolated_prob(tokens, (l1, l2, l3)) for tokens in self.validation_tokens])
                if avg_ppl < best_ppl:
                    best_ppl, best_lambdas = avg_ppl, (l1, l2, l3)
        return best_lambdas, best_ppl
    
if __name__ == "__main__":
    train_path = 'data/train.csv'
    test_path = 'data/test.csv'
    
    # Preprocess data, Build vocabulary, Compute MLEs using Laplace Smoothing
    model = NgramLanguageModel(train_path, test_path)
    
    # Compute perplexities
    perplexity_start_time = time.time()
    unigram_ppl = model.compute_perplexity(model.test_tokens, 'unigram', model.unigram_probs, None)
    bigram_ppl = model.compute_perplexity(model.test_tokens, 'bigram', model.bigram_probs, model.unigram_counts)
    trigram_ppl = model.compute_perplexity(model.test_tokens, 'trigram', model.trigram_probs, model.bigram_context_counts)
    perplexity_end_time = time.time()
    
    # Optimize interpolation
    interpolation_start_time = time.time()
    best_lambdas, best_ppl = model.optimize_interpolation()
    
    # Compute interpolated perplexity on test data
    interp_ppl = np.mean([
        model.interpolated_prob(tokens, best_lambdas) 
        for tokens in model.test_tokens
    ])
    interpolation_end_time = time.time()
    
    # PRINT RESULTS
    print(f"Unigram Perplexity: {unigram_ppl:.2f}")
    print(f"Bigram Perplexity: {bigram_ppl:.2f}")
    print(f"Trigram Perplexity: {trigram_ppl:.2f}")
    print(f"Best Lambdas: {best_lambdas}")
    print(f"Interpolated Perplexity: {interp_ppl:.2f}")

    #Print time taken for each step
    print(f"Perplexity Calculation Time: {(perplexity_end_time - perplexity_start_time):.2f} seconds")
    print(f"Interpolation Optimization Time: {(interpolation_end_time - interpolation_start_time):.2f} seconds")