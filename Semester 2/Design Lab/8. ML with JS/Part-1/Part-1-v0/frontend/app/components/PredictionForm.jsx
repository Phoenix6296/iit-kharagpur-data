// components/PredictionForm.jsx
"use client";

export const PredictionForm = ({
  trainedModels,
  selectedModelType,
  setSelectedModelType,
  inputText,
  setInputText,
  prediction,
  handlePredict,
}) => (
  <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-md mt-6">
    <h2 className="text-xl font-semibold text-gray-700 mb-4">
      Make a Prediction
    </h2>
    <div className="space-y-4">
      <select
        value={selectedModelType}
        onChange={(e) => setSelectedModelType(e.target.value)}
        className="block w-full text-gray-700 border border-gray-300 rounded-lg p-2 focus:ring focus:ring-blue-200 focus:outline-none"
      >
        <option value="" disabled>
          Select a trained model
        </option>
        {Object.keys(trainedModels).map((modelType) => (
          <option key={modelType} value={modelType}>
            {modelType.replace(/_/g, " ").toUpperCase()}
          </option>
        ))}
      </select>

      <textarea
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        placeholder="Enter text to classify..."
        className="block w-full text-gray-700 border border-gray-300 rounded-lg p-2 h-32 focus:ring focus:ring-blue-200 focus:outline-none"
      />

      <button
        onClick={handlePredict}
        disabled={!selectedModelType || !trainedModels[selectedModelType]}
        className={`w-full rounded-lg py-2 font-semibold transition ${
          !selectedModelType
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
  </div>
);
