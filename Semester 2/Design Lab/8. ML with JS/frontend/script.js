document
  .getElementById("uploadForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const fileInput = document.getElementById("file_input").files[0];
    if (!fileInput) return alert("Please upload a file");

    const formData = new FormData();
    formData.append("dataset", fileInput);

    try {
      const response = await fetch("http://localhost:3000/api/upload", {
        method: "POST",
        body: formData,
      });
      const result = await response.json();

      if (result.error) {
        alert("Error: " + result.error);
      } else {
        alert(result.message);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  });

async function predictText() {
  const inputText = document.getElementById("input_text").value;

  try {
    const response = await fetch("http://localhost:3000/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: inputText }),
    });
    const result = await response.json();

    if (result.error) {
      alert("Error: " + result.error);
    } else {
      document.getElementById("output").innerText =
        "Prediction: " + result.prediction;
    }
  } catch (error) {
    console.error("Error:", error);
  }
}
