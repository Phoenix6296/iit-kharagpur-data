const express = require("express");
const multer = require("multer");
const fs = require("fs");
const { parse } = require("csv-parse");

const app = express();
const upload = multer({ dest: "uploads/" });

app.use(express.static(__dirname));
app.use(express.json());

// Global variables for test data
let testData, testLabels;

// CSV Upload Endpoint
app.post("/upload", upload.single("csvFile"), (req, res) => {
  if (!req.file) {
    return res.status(400).send("No file uploaded.");
  }
  const filePath = req.file.path;
  processFile(filePath, (results) => {
    res.json(results);
  });
});

// Predict Endpoint for new text
app.post("/predict", express.json(), async (req, res) => {
  try {
    const { text } = req.body;
    if (!text) {
      return res.status(400).json({ error: "No text provided for prediction" });
    }
    const processedText = preprocessText(text);

    // Load the sentiment pipeline from @xenova/transformers
    const { pipeline } = require("@xenova/transformers");
    const sentiment = await pipeline(
      "sentiment-analysis",
      "Xenova/bert-base-multilingual-uncased-sentiment"
    );
    const result = await sentiment(processedText);

    // Instead of returning 0 or 1, we return a text label:
    // "positive", "negative", or "neutral"
    const modelLabel = result[0].label.toUpperCase();
    let predictedLabel;
    if (modelLabel === "NEUTRAL") {
      predictedLabel = "neutral";
    } else if (modelLabel === "POSITIVE") {
      predictedLabel = "positive";
    } else {
      predictedLabel = "negative";
    }

    res.json({ label: predictedLabel });
  } catch (error) {
    console.error("Error during prediction:", error.message);
    res.status(500).json({ error: "Internal server error during prediction" });
  }
});

// Process the uploaded CSV file
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

// Preprocess and split data (we use only the test split for evaluation)
function preprocessData(data, callback) {
  // Filter out rows with empty tweets or labels
  const cleanData = data.filter((row) => row.tweet && row.label);
  console.log(`Total rows after cleaning: ${cleanData.length}`);

  // Shuffle data and take first 1000 items (for speed)
  const shuffledData = shuffle(cleanData);
  const first1000Items = shuffledData.slice(0, 1000);

  // Split: 70% train, 10% validation, 20% test (we evaluate on test data)
  const trainSize = Math.floor(first1000Items.length * 0.7);
  const valSize = Math.floor(first1000Items.length * 0.1);
  testData = first1000Items.slice(trainSize + valSize);
  console.log(`Test size: ${testData.length}`);

  // Preprocess tweets
  const processedTestData = testData.map((row) => preprocessText(row.tweet));

  // Convert labels: "real" → 1, "fake" → 0
  // (Adjust the condition as needed if your dataset uses a different casing or spelling.)
  testLabels = testData.map((row) =>
    row.label.toLowerCase() === "real" ? 1 : 0
  );

  // Run sentiment classification on test data
  predictSentimentForTestData(processedTestData, testLabels, callback);
}

// Use Xenova Transformers to predict sentiment on each tweet in test data
function predictSentimentForTestData(tweets, actualLabels, callback) {
  (async () => {
    const { pipeline } = require("@xenova/transformers");
    const sentiment = await pipeline(
      "sentiment-analysis",
      "Xenova/bert-base-multilingual-uncased-sentiment"
    );

    let predictions = [];
    let validActualLabels = [];

    for (let i = 0; i < tweets.length; i++) {
      const tweet = tweets[i];
      const result = await sentiment(tweet);
      const predictedLabel = result[0].label.toUpperCase();

      // Skip NEUTRAL predictions for evaluation
      if (predictedLabel === "NEUTRAL") {
        continue;
      }

      // Map sentiment to 1 or 0
      const predictedValue = predictedLabel === "POSITIVE" ? 1 : 0;
      predictions.push(predictedValue);
      validActualLabels.push(actualLabels[i]);
    }

    // If everything was NEUTRAL, handle gracefully
    if (predictions.length === 0) {
      callback({
        accuracy: "0.00%",
        precision: "0.00%",
        recall: "0.00%",
        f1Score: "0.00%",
        confusionMatrix: {
          truePositives: 0,
          falsePositives: 0,
          trueNegatives: 0,
          falseNegatives: 0,
        },
        classReport: {
          positive: { precision: 0, recall: 0, f1Score: 0, support: 0 },
          negative: { precision: 0, recall: 0, f1Score: 0, support: 0 },
        },
      });
      return;
    }

    // Calculate evaluation metrics on non-neutral predictions
    const metrics = calculateMetrics(validActualLabels, predictions);
    callback(displayResults(metrics));
  })().catch((err) => {
    console.error("Error during sentiment prediction:", err.message);
    callback({ error: "Error during sentiment prediction" });
  });
}

// Simple text preprocessing
function preprocessText(text) {
  if (!text) return "";
  text = text.toLowerCase();
  text = text.replace(/https?:\/\/\S+/g, "URL");
  text = text.replace(/@(\w+)/g, "$1");
  text = text.replace(/#(\w+)/g, "$1");
  text = text.replace(/[^\w\s]/g, " ");
  text = text.replace(/\s+/g, " ").trim();
  return text;
}

// Shuffle an array
function shuffle(array) {
  const newArray = [...array];
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
  }
  return newArray;
}

// Updated metrics calculation with macro-average for positive and negative classes
function calculateMetrics(actual, predicted) {
  let tp = 0,
    tn = 0,
    fp = 0,
    fn = 0;

  for (let i = 0; i < actual.length; i++) {
    if (actual[i] === 1 && predicted[i] === 1) tp++;
    else if (actual[i] === 0 && predicted[i] === 1) fp++;
    else if (actual[i] === 0 && predicted[i] === 0) tn++;
    else if (actual[i] === 1 && predicted[i] === 0) fn++;
  }

  const accuracy = (tp + tn) / (tp + tn + fp + fn);

  // Metrics for positive class
  const positivePrecision = tp + fp === 0 ? 0 : tp / (tp + fp);
  const positiveRecall = tp + fn === 0 ? 0 : tp / (tp + fn);
  const positiveF1 =
    positivePrecision + positiveRecall === 0
      ? 0
      : (2 * positivePrecision * positiveRecall) /
        (positivePrecision + positiveRecall);

  // Metrics for negative class
  const negativePrecision = tn + fn === 0 ? 0 : tn / (tn + fn);
  const negativeRecall = tn + fp === 0 ? 0 : tn / (tn + fp);
  const negativeF1 =
    negativePrecision + negativeRecall === 0
      ? 0
      : (2 * negativePrecision * negativeRecall) /
        (negativePrecision + negativeRecall);

  // Macro-average of the two classes
  const precision = (positivePrecision + negativePrecision) / 2;
  const recall = (positiveRecall + negativeRecall) / 2;
  const f1Score = (positiveF1 + negativeF1) / 2;

  return {
    accuracy,
    precision,
    recall,
    f1Score,
    confusionMatrix: {
      truePositives: tp,
      falsePositives: fp,
      trueNegatives: tn,
      falseNegatives: fn,
    },
    classReport: {
      positive: {
        precision: positivePrecision,
        recall: positiveRecall,
        f1Score: positiveF1,
        support: tp + fn,
      },
      negative: {
        precision: negativePrecision,
        recall: negativeRecall,
        f1Score: negativeF1,
        support: tn + fp,
      },
    },
  };
}

// Format metrics for display
function displayResults(metrics) {
  return {
    accuracy: (metrics.accuracy * 100).toFixed(2) + "%",
    precision: (metrics.precision * 100).toFixed(2) + "%",
    recall: (metrics.recall * 100).toFixed(2) + "%",
    f1Score: (metrics.f1Score * 100).toFixed(2) + "%",
    confusionMatrix: metrics.confusionMatrix,
    classReport: metrics.classReport,
  };
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
