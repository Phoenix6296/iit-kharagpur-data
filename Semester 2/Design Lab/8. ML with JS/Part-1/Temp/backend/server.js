const express = require("express");
const multer = require("multer");
const fs = require("fs");
const Papa = require("papaparse");
const KNN = require("ml-knn");
const logisticRegression = require("./models/logistic_regression");
const randomForest = require("./models/random_forest");
const kmeans = require("./models/kmeans");
const decisionTree = require("./models/decision_tree");

const app = express();
const PORT = 3000;

const cors = require("cors");

app.use(cors());
app.use(express.json());
app.use(express.static("frontend"));

const storage = multer.diskStorage({
  destination: "./uploads/",
  filename: (req, file, cb) => cb(null, file.originalname),
});
const upload = multer({ storage });

let dataset = [];
let knnModel;

app.post("/upload", upload.single("dataset"), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No file uploaded." });
  }

  const filePath = req.file.path;
  const fileContent = fs.readFileSync(filePath, "utf8");

  Papa.parse(fileContent, {
    header: true,
    skipEmptyLines: true,
    complete: (result) => {
      if (result.data.length === 0) {
        return res.status(400).json({ error: "CSV file is empty." });
      }

      dataset = result.data.map((row) => ({
        text: row["tweet"] || "",
        label: row["label"] || "",
      }));

      res.json({ message: "Dataset uploaded successfully", dataset });
    },
    error: (error) => {
      res
        .status(500)
        .json({ error: "Error processing CSV file", details: error.message });
    },
  });
});

const trainModel = (model, res) => {
  if (!dataset.length) {
    return res.status(400).json({ error: "Dataset not uploaded" });
  }
  res.json(model.trainModel(dataset));
};

app.post("/train/knn", (_, res) => {
  if (!dataset.length) {
    return res.status(400).json({ error: "Dataset not uploaded" });
  }

  const features = dataset.map((d) => [parseFloat(d.text) || 0]);
  const labels = dataset.map((d) =>
    isNaN(d.label) ? d.label : parseInt(d.label, 10)
  );

  if (!features.length || !labels.length) {
    return res
      .status(400)
      .json({ error: "Dataset is empty or improperly formatted." });
  }

  const trainSize = Math.floor(0.9 * features.length);
  const trainFeatures = features.slice(0, trainSize);
  const trainLabels = labels.slice(0, trainSize);
  const testFeatures = features.slice(trainSize);
  const testLabels = labels.slice(trainSize);

  knnModel = new KNN(trainFeatures, trainLabels, { k: 3 });
  const predictions = testFeatures.map((feat) => knnModel.predict(feat));

  let correct = 0;
  let confusionMatrix = {
    real: { real: 0, fake: 0 },
    fake: { real: 0, fake: 0 },
  };

  predictions.forEach((pred, i) => {
    if (pred === testLabels[i]) correct++;
    confusionMatrix[testLabels[i]][pred]++;
  });

  const accuracy = (correct / testLabels.length) * 100;
  res.json({
    message: "KNN model trained successfully!",
    accuracy: `${accuracy.toFixed(2)}%`,
    confusionMatrix,
  });
});

app.post("/train/logistic-regression", (_, res) =>
  trainModel(logisticRegression, res)
);
app.post("/train/random-forest", (_, res) => trainModel(randomForest, res));
app.post("/train/kmeans", (_, res) => trainModel(kmeans, res));
app.post("/train/decision-tree", (_, res) => trainModel(decisionTree, res));

app.post("/predict/:model", async (req, res) => {
  const { model } = req.params;
  const { text } = req.body;

  if (!text) {
    return res
      .status(400)
      .json({ error: "Text input is required for prediction." });
  }

  let prediction;
  try {
    switch (model) {
      case "knn":
        prediction = knnModel
          ? knnModel.predict([parseFloat(text) || 0])
          : "Model not trained";
        break;
      case "logistic-regression":
        prediction = logisticRegression.predict(text);
        break;
      case "random-forest":
        prediction = randomForest.predict(text);
        break;
      case "kmeans":
        prediction = kmeans.predict(text);
        break;
      case "decision-tree":
        prediction = decisionTree.predict(text);
        break;
      default:
        return res.status(400).json({ error: "Invalid model selected." });
    }
    res.json({ prediction });
  } catch (error) {
    res.status(500).json({ error: "Prediction error", details: error.message });
  }
});

app.listen(PORT, () =>
  console.log(`Server running on http://localhost:${PORT}`)
);
