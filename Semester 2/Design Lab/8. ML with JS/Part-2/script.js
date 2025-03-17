document.getElementById("uploadForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const formData = new FormData(this);
  // No model selection is needed for sentiment analysis
  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Upload successful:", data);
      // Update UI with evaluation results
      document.getElementById("accuracy").textContent = data.accuracy;
      document.getElementById("precision").textContent = data.precision;
      document.getElementById("recall").textContent = data.recall;
      document.getElementById("f1Score").textContent = data.f1Score;

      const reportBody = document.getElementById("reportBody");
      reportBody.innerHTML = "";
      if (data.classReport) {
        for (const [className, metrics] of Object.entries(data.classReport)) {
          const row = reportBody.insertRow();
          row.insertCell().textContent = className;
          row.insertCell().textContent =
            (metrics.precision * 100).toFixed(2) + "%";
          row.insertCell().textContent =
            (metrics.recall * 100).toFixed(2) + "%";
          row.insertCell().textContent =
            (metrics.f1Score * 100).toFixed(2) + "%";
          row.insertCell().textContent = metrics.support;
        }
      }
      document.getElementById("resultsContainer").style.display = "block";
    })
    .catch((error) => {
      console.error("Error during upload:", error.message);
    });
});

document.getElementById("predictBtn").addEventListener("click", function () {
  const text = document.getElementById("predictionInput").value;
  if (!text) {
    alert("Please enter text to predict");
    return;
  }

  fetch("/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text: text }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("predictionClass").textContent = data.label;
      document.getElementById("predictionResult").style.display = "block";
    })
    .catch((error) => {
      console.error("Error during prediction:", error.message);
      alert("Error during prediction: " + error.message);
    });
});
