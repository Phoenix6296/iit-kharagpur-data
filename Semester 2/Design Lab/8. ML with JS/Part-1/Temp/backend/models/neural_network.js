const { NeuralNetwork } = require("brain.js");

function trainModel(dataset) {
  const features = dataset.map((d) => [parseFloat(d.text) || 0]);
  const labels = dataset.map((d) =>
    isNaN(d.label) ? d.label : parseInt(d.label, 10)
  );

  if (!features.length || !labels.length) {
    throw new Error("Dataset is empty or improperly formatted.");
  }

  const net = new NeuralNetwork();
  net.train(
    dataset.map((d) => ({
      input: [parseFloat(d.text) || 0],
      output: { [d.label]: 1 },
    }))
  );

  return { message: "Neural Network trained successfully!" };
}

module.exports = { trainModel };
