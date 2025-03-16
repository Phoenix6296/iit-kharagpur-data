const KMeans = require("ml-kmeans");

function trainModel(dataset) {
  try {
    const features = dataset.map((d) => [parseFloat(d.text) || 0]);

    if (!features.length) {
      throw new Error("Dataset is empty or improperly formatted.");
    }

    const k = 3; // Number of clusters
    const result = KMeans.kmeans(features, k); // FIXED

    return {
      message: "K-Means clustering completed!",
      clusters: result.clusters,
      centroids: result.centroids,
    };
  } catch (error) {
    console.error("K-Means Training Error:", error.message);
    return { error: error.message }; // Ensures JSON response
  }
}

module.exports = { trainModel };
