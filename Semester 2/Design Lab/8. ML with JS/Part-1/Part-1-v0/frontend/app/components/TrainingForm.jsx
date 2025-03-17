// components/TrainingForm.jsx
"use client";
import { useState } from "react";

export const TrainingForm = ({
  modelType,
  setModelType,
  isTraining,
  handleFileUpload,
  trainModel,
}) => (
  <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-md">
    <h2 className="text-xl font-semibold text-gray-700 mb-4">Train a Model</h2>
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
  </div>
);
