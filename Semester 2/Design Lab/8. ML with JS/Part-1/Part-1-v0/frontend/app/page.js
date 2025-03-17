"use client";
import { useState } from "react";
import Papa from "papaparse";
import { Matrix } from "ml-matrix";
import KNN from "ml-knn";
import LogisticRegression from "ml-logistic-regression";
import { DecisionTreeClassifier } from "ml-cart";
import { RandomForestClassifier } from "ml-random-forest";
import { TFIDF } from "./utils/tfidf";
import { TrainingForm } from "./components/TrainingForm";
import { PredictionForm } from "./components/PredictionForm";
import { MetricsTable } from "./components/MetricsTable";

export default function Home() {
  const [file, setFile] = useState(null);
  const [modelType, setModelType] = useState("knn");
  const [trainResult, setTrainResult] = useState(null);
  const [evaluationMetrics, setEvaluationMetrics] = useState(null);
  const [inputText, setInputText] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [isTraining, setIsTraining] = useState(false);
  const [trainedModels, setTrainedModels] = useState({});
  const [selectedModelType, setSelectedModelType] = useState("");

  const handleFileUpload = (event) => setFile(event.target.files[0]);

  const preprocessData = async (file) => {
    const text = await file.text();

    const result = Papa.parse(text, {
      header: true,
      skipEmptyLines: true,
    });

    if (!result.data || result.errors.length) {
      alert("Error parsing CSV. Check file format.");
      return;
    }

    // Extract tweets and labels
    const tweets = [];
    const labels = [];

    result.data.forEach((row) => {
      const tweet = row["tweet"]?.trim();
      const label = row["label"]?.trim().toLowerCase();

      if (tweet && (label === "real" || label === "fake")) {
        tweets.push(tweet);
        labels.push(label);
      }
    });

    if (tweets.length === 0) {
      alert("No valid data found in the CSV.");
      return;
    }

    // Apply TF-IDF transformation
    const tfidf = new TFIDF();
    tfidf.fit(tweets);
    const transformedData = tweets.map((text) => tfidf.transform(text));

    // Shuffle dataset
    const shuffledIndices = [...Array(transformedData.length).keys()].sort(
      () => Math.random() - 0.5
    );
    const shuffledData = shuffledIndices.map((i) => transformedData[i]);
    const shuffledLabels = shuffledIndices.map((i) => labels[i]);

    const trainSize = Math.floor(0.7 * transformedData.length);
    const valSize = Math.floor(0.1 * transformedData.length);

    const trainData = shuffledData.slice(0, trainSize);
    const trainLabels = shuffledLabels.slice(0, trainSize);

    const testData = shuffledData.slice(trainSize + valSize);
    const testLabels = shuffledLabels.slice(trainSize + valSize);

    return { trainData, trainLabels, testData, testLabels, tfidf };
  };

  const trainModel = async (event) => {
    event.preventDefault();
    if (!file) return;
    setIsTraining(true);

    const { trainData, trainLabels, testData, testLabels, tfidf } =
      await preprocessData(file);

    // Convert trainLabels to a proper matrix or a plain array
    const numericLabels = trainLabels.map((label) =>
      label === "real" ? 1 : 0
    );

    let model;
    switch (modelType) {
      case "knn":
        model = new KNN(trainData, numericLabels);
        break;
      case "logistic_regression":
        model = new LogisticRegression();
        model.train(new Matrix(trainData), numericLabels);
        break;
      case "random_forest":
        model = new RandomForestClassifier({ nEstimators: 10 });
        model.train(trainData, numericLabels);
        break;
      case "decision_tree":
        model = new DecisionTreeClassifier();
        model.train(trainData, numericLabels);
        break;
      default:
        return;
    }

    // Save the trained model with its TF-IDF
    setTrainedModels((prev) => ({
      ...prev,
      [modelType]: { model, tfidf },
    }));

    // Generate predictions on test set
    const predictions = testData.map((sample) => model.predict(sample));

    // Compute metrics
    const tp = predictions.filter(
      (pred, i) => pred === 1 && testLabels[i] === "real"
    ).length;
    const tn = predictions.filter(
      (pred, i) => pred === 0 && testLabels[i] === "fake"
    ).length;
    const fp = predictions.filter(
      (pred, i) => pred === 1 && testLabels[i] === "fake"
    ).length;
    const fn = predictions.filter(
      (pred, i) => pred === 0 && testLabels[i] === "real"
    ).length;

    const accuracy = ((tp + tn) / (tp + tn + fp + fn)) * 100;
    const precision = (tp / (tp + fp)) * 100 || 0;
    const recall = (tp / (tp + fn)) * 100 || 0;
    const f1Score = (2 * precision * recall) / (precision + recall) || 0;
    const rocAuc = ((tp / (tp + fn) + tn / (tn + fp)) / 2) * 100 || 0;

    setEvaluationMetrics({
      accuracy,
      precision,
      recall,
      f1Score,
      rocAuc,
      tp,
      tn,
      fp,
      fn,
    });
    setTrainResult(`Model ${modelType} trained successfully!`);
    setIsTraining(false);
  };

  const handlePredict = () => {
    if (!inputText.trim()) {
      alert("Please enter some text.");
      return;
    }

    const modelData = trainedModels[selectedModelType];
    if (!modelData) {
      alert("Please train the selected model first.");
      return;
    }

    const { model, tfidf } = modelData;
    const vector = tfidf.transform(inputText);

    let prediction;
    try {
      switch (selectedModelType) {
        case "knn":
          prediction = model.predict(vector);
          break;
        case "logistic_regression":
          prediction = model.predict(new Matrix([vector]))[0];
          break;
        case "random_forest":
        case "decision_tree":
          prediction = model.predict([vector])[0];
          break;
        default:
          throw new Error("Unknown model type");
      }

      setPrediction(prediction === 1 ? "real" : "fake");
    } catch (error) {
      console.error("Prediction error:", error);
      alert("Prediction failed. Please try again.");
    }
  };

  return (
    <div className="p-6 flex flex-col items-center">
      <TrainingForm
        modelType={modelType}
        setModelType={setModelType}
        isTraining={isTraining}
        handleFileUpload={handleFileUpload}
        trainModel={trainModel}
      />

      <PredictionForm
        trainedModels={trainedModels}
        selectedModelType={selectedModelType}
        setSelectedModelType={setSelectedModelType}
        inputText={inputText}
        setInputText={setInputText}
        prediction={prediction}
        handlePredict={handlePredict}
      />

      {evaluationMetrics && (
        <MetricsTable evaluationMetrics={evaluationMetrics} />
      )}
    </div>
  );
}
