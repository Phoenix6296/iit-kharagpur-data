const KNN = require("ml-knn");

let model = null;

// Convert text to numerical values
function textToVector(text) {
  if (!text) return []; // Prevent errors from undefined values
  return text.split("").map((char) => char.charCodeAt(0));
}

// Train the KNN model
function trainKNN(data, labels, k = 3) {
  if (!data || !labels || data.length === 0 || labels.length === 0) {
    throw new Error("Training data is empty or incorrectly formatted.");
  }

  const vectorizedData = data.map(textToVector);

  if (vectorizedData.some((vec) => vec.length === 0)) {
    throw new Error(
      "Error: Some text entries could not be converted to vectors."
    );
  }

  model = new KNN(vectorizedData, labels, { k });
  console.log("Model trained successfully with", data.length, "samples.");
}

// Predict using the trained model
function predictKNN(inputText) {
  if (!model) throw new Error("Model is not trained yet!");

  const vectorizedInput = textToVector(inputText);
  return model.predict([vectorizedInput])[0];
}

module.exports = { trainKNN, predictKNN };
