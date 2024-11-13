# Frog Species Clustering Using MFCCs

This project involves the analysis and clustering of frog species based on their sound frequencies using the Anuran Calls Dataset. The focus is on employing K-Means clustering as well as other clustering techniques to group the frogs based on their acoustic features (MFCCs).

## Table of Contents
1. [Overview](#overview)
2. [Dataset](#dataset)
3. [Project Structure](#project-structure)
4. [Dependencies](#dependencies)

## Overview
The objective of this project is to cluster frog species based on their audio features derived from Mel-frequency cepstral coefficients (MFCCs). By applying advanced clustering techniques, we aim to improve the understanding of the relationships between different frog species.

## Dataset
The dataset used in this project is the [Anuran Calls Dataset (MFCCs)](https://archive.ics.uci.edu/dataset/406/anuran+calls+mfccs). It contains 22 MFCC coefficients representing the acoustic features of various frog calls along with labels for species classification.

## Project Structure
```plaintext
24CS60R71_Krishna_Biswakarma
├── Part 1
├── Part 2
    ├── report.pdf
    ├── requirements.txt
    ├── Part2_Krishna Biswakarma.ipynb
    ├── Frogs_MFCCs.csv --> Put the dataset here
    └── readme.md

```

## Dependencies
The following libraries are required to run the code:
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn

You can install these libraries using pip:

```bash
pip install -r requirements.txt
```
or 

```bash
pip install pandas numpy matplotlib seaborn scikit-learn
```

