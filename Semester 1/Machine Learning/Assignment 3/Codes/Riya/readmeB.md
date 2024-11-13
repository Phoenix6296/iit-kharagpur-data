# Clustering Frog Species

This project focuses on analyzing and clustering various frog species using their sound frequencies, specifically utilizing the Anuran Calls Dataset. The primary goal is to employ K-Means clustering and other clustering techniques to categorize frogs based on their acoustic characteristics, represented by Mel-frequency cepstral coefficients (MFCCs).

## Project Overview
The aim of this project is to cluster different frog species based on audio features obtained from their calls. By analyzing these features using advanced clustering techniques, we seek to gain insights into the relationships among various frog species.

## Dataset Description
The project utilizes the [Anuran Calls Dataset (MFCCs)](https://archive.ics.uci.edu/dataset/406/anuran+calls+mfccs). This dataset comprises 22 MFCC coefficients that capture the acoustic characteristics of different frog calls, along with corresponding labels for species identification.

```bash
pip install -r requirements.txt
```

## Project Structure
```plaintext
24CS60R70_Riya
├── Part 1
├── Part 2
│   ├── report.pdf
│   ├── requirements.txt
│   ├── part2_Riya.ipynb
│   ├── <dataset>.csv
│   └── readme.md
```

## Data Preprocessing and Exploration
The initial steps involve loading the dataset, performing data preprocessing tasks such as handling missing values and encoding categorical variables, and exploring the data distribution and relationships between features.

## Implementation of K-Means Clustering
The core of the project involves applying the K-Means clustering algorithm to group frog species based on their MFCC features. The number of clusters is determined using techniques like the Elbow Method or Silhouette Score.

## Visualizing Clusters

Visualizing the clusters helps in understanding the grouping of frog species based on their audio features. Techniques like PCA (Principal Component Analysis) can be used for dimensionality reduction and visualization.

## Cluster Evaluation

Evaluating the quality of clusters using metrics like Silhouette Score, Inertia, and Davies-Bouldin Index provides insights into the effectiveness of the clustering algorithm.

## Comparison with Other Clustering Methods

Comparing the results obtained from K-Means clustering with other clustering algorithms like DBSCAN, Agglomerative Clustering can help in selecting the most suitable method for the given dataset.

## Analysis and Findings

Analyzing the clustered groups and identifying patterns or similarities among frog species based on their acoustic features can lead to valuable insights for researchers studying bioacoustics and biodiversity.