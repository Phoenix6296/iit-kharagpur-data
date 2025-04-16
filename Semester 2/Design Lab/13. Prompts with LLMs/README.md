# SST-2 Sentiment Classification with Multiple Prompting Techniques

This project implements sentiment classification on the SST-2 dataset using several prompting strategies with Groq-hosted Large Language Models (LLMs). The notebook demonstrates how to use multiple prompting strategies including:

1. **Zero-Shot Prompting**
2. **Task Explanation Prompting** (using one demonstration example per category)
3. **In-Context Prompting** (using two similar examples from the train set)
4. **Zero-Shot Chain-of-Thought Prompting** (forcing the model to "think step-by-step")
5. **Few-Shot Chain-of-Thought Prompting** (using similar examples with short explanations)

For each strategy, predictions are collected on 20 randomly sampled validation sentences from the SST-2 dataset, and standard classification metrics (accuracy, precision, recall, F1 score) are computed for each of the following models:

- `llama-3.1-8b-instant`
- `Gemma2-9b-it`
- `deepseek-r1-distill-llama-70b`
- `qwen-qwq-32b`

## Project Structure

- **24CS60R71.ipynb**: The main Jupyter Notebook that implements the various prompting techniques and evaluation metrics.
- **24CS60R71.md**: This file providing an overview, setup instructions, and usage details.

## Prerequisites

Before running the notebook, make sure you have Python 3 installed and then install the following dependencies:

```bash
pip install requests datasets scikit-learn
```

## Setup and Running the Notebook

1. **Clone or Download the Project**  
   Clone the repository or download the notebook file `sst2_sentiment_prompting.ipynb`.

2. **Configure the API Key**  
   The notebook uses a placeholder Groq API key:
   ```
   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
   ```
   If you wish to use the actual Groq API, update the `GROQ_API_KEY` variable in the notebook and set the `SIMULATE` flag to `False` in the code.

3. **Open the Notebook**  
   Launch Jupyter Notebook or JupyterLab, then open `sst2_sentiment_prompting.ipynb`.

4. **Run the Notebook**  
   Execute the notebook cells sequentially to:
   - Load the SST-2 dataset.
   - Generate prompt messages for each prompting strategy.
   - Simulate or call the Groq API to obtain predictions.
   - Compute and display evaluation metrics (accuracy, precision, recall, F1 score).

## Notes

- **Simulation Mode:**  
  The notebook is configured to simulate responses using a simple heuristic. Set `SIMULATE = False` to perform actual API calls if you have access to Groq-hosted LLMs.

- **API Endpoint Adjustments:**  
  Make sure to update the API endpoint URL and payload in the `call_groq_model` function based on Groq's latest API documentation if you plan to use the real service.

- **Dataset:**  
  The SST-2 dataset is loaded from the Hugging Face Datasets library under the `glue` dataset with the `sst2` configuration.

## License

This project is provided for educational and research purposes. Modify and use it according to your needs.

## Contact

If you have any questions or suggestions, please open an issue or contact the project maintainer.