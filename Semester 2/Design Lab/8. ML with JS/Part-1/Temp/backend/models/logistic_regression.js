const LogisticRegression = require("ml-logistic-regression");

function trainModel(dataset) {
  try {
    const features = dataset.map((d) => [parseFloat(d.text) || 0]);
    const labels = dataset.map((d) => parseInt(d.label, 10));

    if (!features.length || !labels.length) {
      throw new Error("Dataset is empty or improperly formatted.");
    }

    const model = new LogisticRegression({
      numSteps: 1000,
      learningRate: 5e-3,
    });
    model.train(features, labels);

    return { message: "Logistic Regression model trained successfully!" };
  } catch (error) {
    console.error("Logistic Regression Training Error:", error.message);
    return { error: error.message }; // Ensures JSON response
  }
}

module.exports = { trainModel };
