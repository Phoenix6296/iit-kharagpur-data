"use client";
import KNN from "ml-knn";
import LogisticRegression from "ml-logistic-regression";
import { DecisionTreeClassifier } from "ml-cart";
import { RandomForestClassifier } from "ml-random-forest";
import { useState } from "react";
import Papa from "papaparse";
import { Matrix } from "ml-matrix";

// Custom TF-IDF Implementation
class TFIDF {
  constructor() {
    this.documents = [];
    this.termFreqs = [];
    this.idfScores = {};
  }

  tokenize(text) {
    return text.toLowerCase().match(/\b\w+\b/g) || [];
  }

  computeTF(words) {
    const tf = {};
    words.forEach((word) => {
      tf[word] = (tf[word] || 0) + 1;
    });
    const totalWords = words.length;
    Object.keys(tf).forEach((word) => {
      tf[word] /= totalWords;
    });
    return tf;
  }

  computeIDF() {
    const totalDocs = this.documents.length;
    const docFrequency = {};

    this.documents.forEach((words) => {
      const uniqueWords = new Set(words);
      uniqueWords.forEach((word) => {
        docFrequency[word] = (docFrequency[word] || 0) + 1;
      });
    });

    Object.keys(docFrequency).forEach((word) => {
      this.idfScores[word] = Math.log(totalDocs / (docFrequency[word] + 1));
    });
  }

  fit(documents) {
    this.documents = documents.map(this.tokenize);
    this.termFreqs = this.documents.map((doc) => this.computeTF(doc));
    this.computeIDF();
  }

  transform(text) {
    const words = this.tokenize(text);
    const tf = this.computeTF(words);
    const tfidfVector = {};

    Object.keys(tf).forEach((word) => {
      if (this.idfScores[word] !== undefined) {
        tfidfVector[word] = tf[word] * this.idfScores[word];
      }
    });

    return Object.values(tfidfVector);
  }
}

export default function Home() {
  const [file, setFile] = useState(null);
  const [modelType, setModelType] = useState("knn");
  const [trainResult, setTrainResult] = useState(null);
  const [evaluationMetrics, setEvaluationMetrics] = useState(null);
  const [inputText, setInputText] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [isTraining, setIsTraining] = useState(false);
  const [trainedModel, setTrainedModel] = useState(null);

  // Convert trainLabels to a proper matrix or a plain array
  const tfidf = new TFIDF();

  const handleFileUpload = (event) => {
    setFile(event.target.files[0]);
  };

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

    console.log("Tweets:", tweets);
    console.log("Labels:", labels);

    // Apply TF-IDF transformation
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

    return { trainData, trainLabels, testData, testLabels };
  };

  const trainModel = async (event) => {
    event.preventDefault();
    if (!file) return;
    setIsTraining(true);

    const { trainData, trainLabels, testData, testLabels } =
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

    // Save the trained model
    setTrainedModel(model);

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

  // const handlePredict = () => {
  //   if (!trainedModel || !inputText.trim()) {
  //     alert("Please train a model and enter text to predict.");
  //     return;
  //   }

  //   try {
  //     // Transform input text using TF-IDF
  //     const transformedInput = tfidf.transform(inputText);

  //     // Make prediction
  //     const numericPrediction = trainedModel.predict(transformedInput);

  //     // Convert numeric prediction back to label
  //     const predictedLabel = numericPrediction === 1 ? "real" : "fake";

  //     // Set prediction result
  //     setPrediction(predictedLabel);
  //   } catch (error) {
  //     console.error("Prediction error:", error);
  //     alert(
  //       "Error making prediction. Make sure you've trained a model with valid data."
  //     );
  //   }
  // };

  return (
    <div className="p-6 flex flex-col items-center">
      <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">
          Train a Model
        </h2>
        <form className="space-y-4" onSubmit={trainModel}>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            className="block w-full text-gray-700 border border-gray-300 rounded-lg p-2 focus:ring focus:ring-blue-200 focus:outline-none"
          />
          <select
            value={modelType}
            onChange={(e) => setModelType(e.target.value)}
            className="block w-full text-gray-700 border border-gray-300 rounded-lg p-2 focus:ring focus:ring-blue-200 focus:outline-none"
          >
            <option value="knn">KNN</option>
            <option value="logistic_regression">Logistic Regression</option>
            <option value="random_forest">Random Forest</option>
            <option value="decision_tree">Decision Tree</option>
          </select>
          <button
            type="submit"
            className={`w-full rounded-lg py-2 font-semibold transition ${
              isTraining
                ? "bg-gray-500 cursor-not-allowed"
                : "bg-blue-600 text-white hover:bg-blue-700 cursor-pointer"
            }`}
            disabled={isTraining}
          >
            {isTraining ? "Training..." : "Train"}
          </button>
        </form>
        {trainResult && (
          <p className="mt-4 text-green-600 font-semibold">{trainResult}</p>
        )}
      </div>

      {/* Prediction Input Box */}
      {/* <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-md mt-6">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">
          Make a Prediction
        </h2>
        <div className="space-y-4">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Enter text to classify..."
            className="block w-full text-gray-700 border border-gray-300 rounded-lg p-2 h-32 focus:ring focus:ring-blue-200 focus:outline-none"
          />
          <button
            onClick={handlePredict}
            disabled={!trainedModel}
            className={`w-full rounded-lg py-2 font-semibold transition ${
              !trainedModel
                ? "bg-gray-500 cursor-not-allowed"
                : "bg-blue-600 text-white hover:bg-blue-700 cursor-pointer"
            }`}
          >
            Predict
          </button>
        </div>
        {prediction && (
          <div className="mt-4">
            <p className="font-semibold text-gray-700">Prediction Result:</p>
            <div
              className={`p-3 mt-2 rounded-lg font-bold text-center ${
                prediction === "real"
                  ? "bg-green-100 text-green-800"
                  : "bg-red-100 text-red-800"
              }`}
            >
              {prediction.toUpperCase()}
            </div>
          </div>
        )}
      </div> */}

      {evaluationMetrics && (
        <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-md mt-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            Model Evaluation Metrics
          </h2>
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-200">
                <th className="border border-gray-300 p-2 text-left">Metric</th>
                <th className="border border-gray-300 p-2 text-left">Value</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(evaluationMetrics).map(([key, value]) => (
                <tr key={key} className="odd:bg-white even:bg-gray-100">
                  <td className="border border-gray-300 p-2">{key}</td>
                  <td className="border border-gray-300 p-2 font-semibold">
                    {value.toFixed(4)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
