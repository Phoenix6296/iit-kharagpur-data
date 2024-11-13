# Support Vector Machine Classifier on the HIGGS Dataset

This project implements Support Vector Machine (SVM) models on the HIGGS dataset to classify events as signal or background, aiming to analyze and predict the presence of a Higgs boson particle. We explore various SVM kernels and perform hyperparameter tuning to optimize model performance.

## Overview
The primary objective of this project is to analyze the Higgs Boson dataset, extract insights, and utilize SVM classifiers to understand patterns and relationships within the data. This analysis provides valuable insights into particle physics and contributes to the ongoing research surrounding the Higgs boson.

## Dataset
The dataset used in this project is the [HIGGS Dataset](https://archive.ics.uci.edu/dataset/280/higgs). This dataset contains features related to particle collision events, and each event is labeled as either a signal (Higgs boson) or background.

## Project Structure
```plaintext
24CS60R70_Riya
├── Part 1
│   ├── report.pdf
│   ├── requirements.txt
│   ├── part1_Riya.ipynb
│   ├── <dataset>.csv
│   └── readme.md
└── Part 2
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage
1. Place the HIGGS dataset in the appropriate directory.
2. Run the Jupyter notebook `part1_Riya.ipynb` to train and evaluate the SVM models.
3. Analyze the results and explore the insights obtained from the dataset.

## Methodology
1. Data Preprocessing: Exploratory Data Analysis (EDA), feature scaling, and data visualization.
2. Model Selection: Experimenting with different SVM kernels (linear, polynomial, radial basis function) and hyperparameters.
3. Model Evaluation: Cross-validation, performance metrics (accuracy, precision, recall, F1-score), and ROC curves.
4. Hyperparameter Tuning: Grid search and random search for optimizing model performance.

## Results
The SVM models achieved an accuracy of X% on the test set, with the linear kernel outperforming the other kernels. The hyperparameter tuning process improved the model's performance by Y%.

## Future Work
1. Implement ensemble methods (e.g., Random Forest, Gradient Boosting) for comparison.
2. Explore feature engineering techniques to enhance model performance.
3. Investigate advanced SVM techniques (e.g., one-class SVM, nu-SVM) for anomaly detection.

## Acknowledgments
- [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/280/higgs) for providing the HIGGS dataset.

