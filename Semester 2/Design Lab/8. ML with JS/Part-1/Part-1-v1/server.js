const express = require("express");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const { parse } = require("csv-parse");
const KNN = require("ml-knn");
const LogisticRegression = require("ml-logistic-regression");
const RandomForestClassifier =
  require("ml-random-forest").RandomForestClassifier;
const DecisionTreeClassifier = require("ml-cart").DecisionTreeClassifier;
const tf = require("@tensorflow/tfjs");

const { kmeans } = require("ml-kmeans");
let kmeansClusters;
let kmeansTrainLabels;

const app = express();
const upload = multer({ dest: "uploads/" });

//app.use(express.static('public'));
app.use(express.static(__dirname));

// Global variables
let trainData, valData, testData;
let trainLabels, valLabels, testLabels;
let tfidfVectorizer;
let knnModel;
let model;
let modelType;

// Define the calculateDistance function
function calculateDistance(vec1, vec2) {
  return Math.sqrt(
    vec1.reduce((acc, val, idx) => acc + Math.pow(val - vec2[idx], 2), 0)
  );
}

app.post("/upload", upload.single("csvFile"), (req, res) => {
  if (!req.file) {
    return res.status(400).send("No file uploaded.");
  }

  const filePath = req.file.path;
  modelType = req.body.model[0]; // Access model type from request body

  if (!modelType) {
    return res.status(400).send("Model type not specified.");
  }
  processFile(filePath, (results) => {
    res.json(results);
  });
});

app.post("/predict", express.json(), (req, res) => {
  try {
    const { text } = req.body;
    if (!text) {
      return res.status(400).json({ error: "No text provided for prediction" });
    }
    console.log("Text to predict:", text);

    const processedText = preprocessText(text);
    console.log("Processed text:", processedText);

    const tfidfVector = tfidfVectorizer.transform([processedText])[0];
    console.log("TF-IDF vector:", tfidfVector);

    if (modelType === "Kmeans_cluster") {
      console.log("Hwllo from k means cluster");
      let closestClusterIndex = -1;
      let minDistance = Infinity;
      for (let i = 0; i < kmeansClusters.centroids.length; i++) {
        const distance = calculateDistance(
          tfidfVector,
          kmeansClusters.centroids[i]
        );
        if (distance < minDistance) {
          minDistance = distance;
          closestClusterIndex = i;
        }
      }

      // Assign labels to clusters
      const clusterLabels = [];
      for (let i = 0; i < kmeansClusters.centroids.length; i++) {
        const clusterIndices = kmeansClusters.clusters
          .map((val, idx) => (val === i ? idx : null))
          .filter((val) => val !== null);
        const clusterLabelsInCluster = clusterIndices.map(
          (idx) => kmeansTrainLabels[idx]
        );

        const labelCounts = {};
        clusterLabelsInCluster.forEach((label) => {
          labelCounts[label] = (labelCounts[label] || 0) + 1;
        });
        const majorityLabel = Object.keys(labelCounts).reduce((a, b) =>
          labelCounts[a] > labelCounts[b] ? a : b
        );
        clusterLabels.push(majorityLabel);
      }

      console.log(closestClusterIndex, "closestClusterIndex");
      console.log(
        clusterLabels[closestClusterIndex],
        "clusterLabels[closestClusterIndex] "
      );

      const predictedLabel =
        clusterLabels[closestClusterIndex] === "1" ? "real" : "fake";
      console.log(`Predicted Label for New Tweet: ${predictedLabel}`);
      res.json({ label: predictedLabel });
    } else if (modelType === "neural_network") {
      const inputTensor = tf.tensor2d([tfidfVector]);
      const predictionTensor = model.predict(inputTensor);
      const predictionValue = Array.from(predictionTensor.dataSync())[0];
      const label = predictionValue > 0.5 ? "real" : "fake";

      console.log("Predicted label:", label);
      res.json({ label });
    } else {
      const prediction = model.predict([tfidfVector])[0];
      //const prediction = knnModel.predict([tfidfVector])[0];
      const label = prediction === 1 ? "real" : "fake";
      console.log("Predicted label:", label);
      res.json({ label });
    }
  } catch (error) {
    console.error("Error during prediction:", error.message);
    res.status(500).json({ error: "Internal server error during prediction" });
  }
});

function processFile(filePath, callback) {
  fs.readFile(filePath, "utf8", (err, fileContent) => {
    if (err) {
      console.error("Error reading file:", err);
      return callback({ error: "Error reading file" });
    }

    parse(fileContent, { columns: true }, (err, data) => {
      if (err) {
        console.error("Error parsing CSV:", err);
        return callback({ error: "Error parsing CSV" });
      }

      console.log("File parsed successfully");
      preprocessData(data, callback);
    });
  });
}

function preprocessData(data, callback) {
  // Filter out rows with empty tweets or labels
  const cleanData = data.filter((row) => row.tweet && row.label);
  console.log(`Total rows after cleaning: ${cleanData.length}`);

  // Shuffle data
  const shuffledData = shuffle(cleanData);
  const first1000Items = shuffledData.slice(0, 1000);
  // Split data: 70% train, 10% validation, 20% test
  const trainSize = Math.floor(first1000Items.length * 0.7);
  const valSize = Math.floor(first1000Items.length * 0.1);

  trainData = first1000Items.slice(0, trainSize);
  valData = first1000Items.slice(trainSize, trainSize + valSize);
  testData = first1000Items.slice(trainSize + valSize);

  console.log(
    `Train size: ${trainData.length}, Val size: ${valData.length}, Test size: ${testData.length}`
  );

  // Extract tweets and labels
  const processedTrainData = trainData.map((row) => preprocessText(row.tweet));
  const processedValData = valData.map((row) => preprocessText(row.tweet));
  const processedTestData = testData.map((row) => preprocessText(row.tweet));

  trainLabels = trainData.map((row) => (row.label === "real" ? 1 : 0));
  valLabels = valData.map((row) => (row.label === "real" ? 1 : 0));
  testLabels = testData.map((row) => (row.label === "real" ? 1 : 0));

  // Apply TF-IDF
  tfidfVectorizer = new TfidfVectorizer();
  const trainTfidf = tfidfVectorizer.fitTransform(processedTrainData);
  const valTfidf = tfidfVectorizer.transform(processedValData);
  const testTfidf = tfidfVectorizer.transform(processedTestData);

  // Train model
  trainModel(
    trainTfidf,
    trainLabels,
    valTfidf,
    valLabels,
    testTfidf,
    testLabels,
    callback
  );
}

function trainModel(
  trainTfidf,
  trainLabels,
  valTfidf,
  valLabels,
  testTfidf,
  testLabels,
  callback
) {
  console.log("Model Type", modelType);
  if (modelType === "knn") {
    model = new KNN(trainTfidf, trainLabels, { k: 8 });
  } else if (modelType === "logistic_regression") {
    model = new LogisticRegression(trainTfidf, trainLabels);
  } else if (modelType === "random_forest") {
    const options = {
      seed: 3,
      maxFeatures: 0.5, // Reduce max features to speed up training
      replacement: true,
      nEstimators: 10, // Reduce the number of estimators for faster training
    };
    model = new RandomForestClassifier(options);
    model.train(trainTfidf, trainLabels);
  } else if (modelType === "decision_Tree") {
    const options2 = {
      gainFunction: "gini",
      maxDepth: 10,
      minNumSamples: 3,
    };
    model = new DecisionTreeClassifier(options2);
    model.train(trainTfidf, trainLabels);
  } else if (modelType === "neural_network") {
    async function trainNeuralNetwork() {
      const model = tf.sequential();
      model.add(
        tf.layers.dense({
          units: 128,
          inputShape: [trainTfidf[0].length],
          activation: "relu",
        })
      );
      model.add(tf.layers.dense({ units: 64, activation: "relu" }));
      model.add(tf.layers.dense({ units: 1, activation: "sigmoid" }));

      // Compile the model
      model.compile({
        optimizer: tf.train.adam(),
        loss: "binaryCrossentropy",
        metrics: ["accuracy"],
      });

      // Convert data to tensors
      const xs = tf.tensor2d(trainTfidf);
      const ys = tf.tensor2d(trainLabels.map((label) => [label]));

      console.log("Training neural network...");
      await model.fit(xs, ys, {
        epochs: 50,
        batchSize: 32,
        validationData: [
          tf.tensor2d(valTfidf),
          tf.tensor2d(valLabels.map((label) => [label])),
        ],
        callbacks: {
          onEpochEnd: (epoch, logs) => {
            console.log(
              `Epoch ${epoch + 1}: Loss = ${logs.loss}, Accuracy = ${logs.acc}`
            );
          },
        },
      });
      console.log("Neural network training complete.");

      return model;
    }

    trainNeuralNetwork()
      .then((trainedModel) => {
        model = trainedModel; // Save trained model globally for predictions
        console.log("Neural network training complete.");
      })
      .catch((err) => {
        console.error("Error during neural network training:", err.message);
      });
  } else if (modelType === "Kmeans_cluster") {
    const clusters = kmeans(trainTfidf, 2);
    kmeansClusters = clusters;
    kmeansTrainLabels = trainLabels;
    console.log("KMeans Clusters:", clusters);
  } else {
    console.error("Unsupported model type");
    return callback({ error: "Unsupported model type" });
  }

  console.log("Training done");
  // Evaluate on test data
  if (modelType === "Kmeans_cluster") {
    console.log("it is kmeans no prediction");
  } else if (modelType === "neural_network") {
    const predictionsTensor = model.predict(tf.tensor2d(testTfidf));
    const predictionsArray = Array.from(predictionsTensor.dataSync()).map(
      (pred) => (pred > 0.5 ? 1 : 0)
    );

    // Calculate metrics
    const metrics = calculateMetrics(testLabels, predictionsArray);

    // Return results
    callback(displayResults(metrics));
  } else {
    const predictions = testTfidf.map((vec) => model.predict([vec])[0]);

    // Calculate metrics
    const metrics = calculateMetrics(testLabels, predictions);

    // Return results
    callback(displayResults(metrics));
  }
}

// Text preprocessing function
function preprocessText(text) {
  if (!text) return "";

  // Convert to lowercase
  text = text.toLowerCase();

  // Replace URLs
  text = text.replace(/https?:\/\/\S+/g, "URL");

  // Handle mentions
  text = text.replace(/@(\w+)/g, "$1");

  // Remove hashtags
  text = text.replace(/#(\w+)/g, "$1");

  // Remove punctuation
  text = text.replace(/[^\w\s]/g, " ");

  // Remove extra spaces
  text = text.replace(/\s+/g, " ").trim();

  return text;
}

// Shuffle array function
function shuffle(array) {
  const newArray = [...array];
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
  }
  return newArray;
}

// Calculate metrics
function calculateMetrics(actual, predicted) {
  const truePositives = actual.filter(
    (val, idx) => val === 1 && predicted[idx] === 1
  ).length;
  const falsePositives = actual.filter(
    (val, idx) => val === 0 && predicted[idx] === 1
  ).length;
  const trueNegatives = actual.filter(
    (val, idx) => val === 0 && predicted[idx] === 0
  ).length;
  const falseNegatives = actual.filter(
    (val, idx) => val === 1 && predicted[idx] === 0
  ).length;

  const accuracy = (truePositives + trueNegatives) / actual.length;
  const precision = truePositives / (truePositives + falsePositives) || 0;
  const recall = truePositives / (truePositives + falseNegatives) || 0;
  const f1Score = (2 * (precision * recall)) / (precision + recall) || 0;

  // Precision, recall, f1-score for each class
  const realPrecision = truePositives / (truePositives + falsePositives) || 0;
  const realRecall = truePositives / (truePositives + falseNegatives) || 0;
  const realF1 =
    (2 * (realPrecision * realRecall)) / (realPrecision + realRecall) || 0;

  const fakePrecision = trueNegatives / (trueNegatives + falseNegatives) || 0;
  const fakeRecall = trueNegatives / (trueNegatives + falsePositives) || 0;
  const fakeF1 =
    (2 * (fakePrecision * fakeRecall)) / (fakePrecision + fakeRecall) || 0;

  return {
    accuracy,
    precision,
    recall,
    f1Score,
    confusionMatrix: {
      truePositives,
      falsePositives,
      trueNegatives,
      falseNegatives,
    },
    classReport: {
      real: {
        precision: realPrecision,
        recall: realRecall,
        f1Score: realF1,
        support: truePositives + falseNegatives,
      },
      fake: {
        precision: fakePrecision,
        recall: fakeRecall,
        f1Score: fakeF1,
        support: trueNegatives + falsePositives,
      },
    },
  };
}

function displayResults(metrics) {
  return {
    accuracy: (metrics.accuracy * 100).toFixed(2) + "%",
    precision: (metrics.precision * 100).toFixed(2) + "%",
    recall: (metrics.recall * 100).toFixed(2) + "%",
    classReport: {
      real: metrics.classReport.real,
      fake: metrics.classReport.fake,
    },
  };
}

// TF-IDF implementation
class TfidfVectorizer {
  constructor() {
    this.vocabulary = {};
    this.idf = {};
    this.documentCount = 0;
    this.vocabularySize = 0;
  }

  fit(documents) {
    this.documentCount = documents.length;
    const docFreq = {};

    documents.forEach((doc) => {
      const terms = doc.split(" ");
      const uniqueTerms = [...new Set(terms)];

      uniqueTerms.forEach((term) => {
        if (term.length > 1) {
          if (!this.vocabulary.hasOwnProperty(term)) {
            this.vocabulary[term] = this.vocabularySize++;
          }
          docFreq[term] = (docFreq[term] || 0) + 1;
        }
      });
    });

    for (const term in docFreq) {
      this.idf[term] =
        Math.log((this.documentCount + 1) / (docFreq[term] + 1)) + 1;
    }

    return this;
  }

  transform(documents) {
    return documents.map((doc) => {
      const vector = new Array(this.vocabularySize).fill(0);
      const terms = doc.split(" ");
      const termFreq = {};

      terms.forEach((term) => {
        if (term.length > 1 && this.vocabulary.hasOwnProperty(term)) {
          termFreq[term] = (termFreq[term] || 0) + 1;
        }
      });

      for (const term in termFreq) {
        const tf = termFreq[term];
        const idx = this.vocabulary[term];
        vector[idx] = tf * (this.idf[term] || 0);
      }

      return vector;
    });
  }

  fitTransform(documents) {
    this.fit(documents);
    return this.transform(documents);
  }
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
