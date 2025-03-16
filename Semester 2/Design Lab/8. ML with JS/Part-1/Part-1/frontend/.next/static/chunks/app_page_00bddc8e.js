(globalThis.TURBOPACK = globalThis.TURBOPACK || []).push(["static/chunks/app_page_00bddc8e.js", {

"[project]/app/page.js [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { g: global, __dirname, k: __turbopack_refresh__, m: module } = __turbopack_context__;
{
__turbopack_context__.s({
    "default": (()=>Home)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$knn$2f$src$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/ml-knn/src/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$logistic$2d$regression$2f$src$2f$logreg$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/ml-logistic-regression/src/logreg.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$cart$2f$src$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$module__evaluation$3e$__ = __turbopack_context__.i("[project]/node_modules/ml-cart/src/index.js [app-client] (ecmascript) <module evaluation>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$cart$2f$src$2f$DecisionTreeClassifier$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/ml-cart/src/DecisionTreeClassifier.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$random$2d$forest$2f$src$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$module__evaluation$3e$__ = __turbopack_context__.i("[project]/node_modules/ml-random-forest/src/index.js [app-client] (ecmascript) <module evaluation>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$random$2d$forest$2f$src$2f$RandomForestClassifier$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/ml-random-forest/src/RandomForestClassifier.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$papaparse$2f$papaparse$2e$min$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/papaparse/papaparse.min.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$matrix$2f$matrix$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/ml-matrix/matrix.mjs [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
;
;
;
// Custom TF-IDF Implementation
class TFIDF {
    constructor(){
        this.documents = [];
        this.termFreqs = [];
        this.idfScores = {};
    }
    tokenize(text) {
        return text.toLowerCase().match(/\b\w+\b/g) || [];
    }
    computeTF(words) {
        const tf = {};
        words.forEach((word)=>{
            tf[word] = (tf[word] || 0) + 1;
        });
        const totalWords = words.length;
        Object.keys(tf).forEach((word)=>{
            tf[word] /= totalWords;
        });
        return tf;
    }
    computeIDF() {
        const totalDocs = this.documents.length;
        const docFrequency = {};
        this.documents.forEach((words)=>{
            const uniqueWords = new Set(words);
            uniqueWords.forEach((word)=>{
                docFrequency[word] = (docFrequency[word] || 0) + 1;
            });
        });
        Object.keys(docFrequency).forEach((word)=>{
            this.idfScores[word] = Math.log(totalDocs / (docFrequency[word] + 1));
        });
    }
    fit(documents) {
        this.documents = documents.map(this.tokenize);
        this.termFreqs = this.documents.map((doc)=>this.computeTF(doc));
        this.computeIDF();
    }
    transform(text) {
        const words = this.tokenize(text);
        const tf = this.computeTF(words);
        const tfidfVector = {};
        Object.keys(tf).forEach((word)=>{
            if (this.idfScores[word] !== undefined) {
                tfidfVector[word] = tf[word] * this.idfScores[word];
            }
        });
        return Object.values(tfidfVector);
    }
}
function Home() {
    _s();
    const [file, setFile] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [modelType, setModelType] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("knn");
    const [trainResult, setTrainResult] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [evaluationMetrics, setEvaluationMetrics] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [inputText, setInputText] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [prediction, setPrediction] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [isTraining, setIsTraining] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [trainedModels, setTrainedModels] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({});
    const [selectedModelType, setSelectedModelType] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const handleFileUpload = (event)=>{
        setFile(event.target.files[0]);
    };
    const preprocessData = async (file)=>{
        const text = await file.text();
        const result = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$papaparse$2f$papaparse$2e$min$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].parse(text, {
            header: true,
            skipEmptyLines: true
        });
        if (!result.data || result.errors.length) {
            alert("Error parsing CSV. Check file format.");
            return;
        }
        // Extract tweets and labels
        const tweets = [];
        const labels = [];
        result.data.forEach((row)=>{
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
        // Apply TF-IDF transformation
        const tfidf = new TFIDF();
        tfidf.fit(tweets);
        const transformedData = tweets.map((text)=>tfidf.transform(text));
        // Shuffle dataset
        const shuffledIndices = [
            ...Array(transformedData.length).keys()
        ].sort(()=>Math.random() - 0.5);
        const shuffledData = shuffledIndices.map((i)=>transformedData[i]);
        const shuffledLabels = shuffledIndices.map((i)=>labels[i]);
        const trainSize = Math.floor(0.7 * transformedData.length);
        const valSize = Math.floor(0.1 * transformedData.length);
        const trainData = shuffledData.slice(0, trainSize);
        const trainLabels = shuffledLabels.slice(0, trainSize);
        const testData = shuffledData.slice(trainSize + valSize);
        const testLabels = shuffledLabels.slice(trainSize + valSize);
        return {
            trainData,
            trainLabels,
            testData,
            testLabels,
            tfidf
        };
    };
    const trainModel = async (event)=>{
        event.preventDefault();
        if (!file) return;
        setIsTraining(true);
        const { trainData, trainLabels, testData, testLabels, tfidf } = await preprocessData(file);
        // Convert trainLabels to a proper matrix or a plain array
        const numericLabels = trainLabels.map((label)=>label === "real" ? 1 : 0);
        let model;
        switch(modelType){
            case "knn":
                model = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$knn$2f$src$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"](trainData, numericLabels);
                break;
            case "logistic_regression":
                model = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$logistic$2d$regression$2f$src$2f$logreg$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"]();
                model.train(new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$matrix$2f$matrix$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Matrix"](trainData), numericLabels);
                break;
            case "random_forest":
                model = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$random$2d$forest$2f$src$2f$RandomForestClassifier$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["RandomForestClassifier"]({
                    nEstimators: 10
                });
                model.train(trainData, numericLabels);
                break;
            case "decision_tree":
                model = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$cart$2f$src$2f$DecisionTreeClassifier$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DecisionTreeClassifier"]();
                model.train(trainData, numericLabels);
                break;
            default:
                return;
        }
        // Save the trained model with its TF-IDF
        setTrainedModels((prev)=>({
                ...prev,
                [modelType]: {
                    model,
                    tfidf
                }
            }));
        // Generate predictions on test set
        const predictions = testData.map((sample)=>model.predict(sample));
        // Compute metrics
        const tp = predictions.filter((pred, i)=>pred === 1 && testLabels[i] === "real").length;
        const tn = predictions.filter((pred, i)=>pred === 0 && testLabels[i] === "fake").length;
        const fp = predictions.filter((pred, i)=>pred === 1 && testLabels[i] === "fake").length;
        const fn = predictions.filter((pred, i)=>pred === 0 && testLabels[i] === "real").length;
        const accuracy = (tp + tn) / (tp + tn + fp + fn) * 100;
        const precision = tp / (tp + fp) * 100 || 0;
        const recall = tp / (tp + fn) * 100 || 0;
        const f1Score = 2 * precision * recall / (precision + recall) || 0;
        const rocAuc = (tp / (tp + fn) + tn / (tn + fp)) / 2 * 100 || 0;
        setEvaluationMetrics({
            accuracy,
            precision,
            recall,
            f1Score,
            rocAuc,
            tp,
            tn,
            fp,
            fn
        });
        setTrainResult(`Model ${modelType} trained successfully!`);
        setIsTraining(false);
    };
    const handlePredict = ()=>{
        if (!inputText.trim()) {
            alert("Please enter some text.");
            return;
        }
        const modelData = trainedModels[selectedModelType];
        if (!modelData) {
            alert("Please train the selected model first.");
            return;
        }
        const { model, tfidf } = modelData;
        const vector = tfidf.transform(inputText);
        let prediction;
        try {
            switch(selectedModelType){
                case "knn":
                    prediction = model.predict(vector);
                    break;
                case "logistic_regression":
                    prediction = model.predict(new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$matrix$2f$matrix$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Matrix"]([
                        vector
                    ]))[0];
                    break;
                case "random_forest":
                case "decision_tree":
                    prediction = model.predict([
                        vector
                    ])[0];
                    break;
                default:
                    throw new Error("Unknown model type");
            }
            setPrediction(prediction === 1 ? "real" : "fake");
        } catch (error) {
            console.error("Prediction error:", error);
            alert("Prediction failed. Please try again.");
        }
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "p-6 flex flex-col items-center",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "bg-white shadow-lg rounded-lg p-6 w-full max-w-md",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                        className: "text-xl font-semibold text-gray-700 mb-4",
                        children: "Train a Model"
                    }, void 0, false, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 263,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                        className: "space-y-4",
                        onSubmit: trainModel,
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                type: "file",
                                accept: ".csv",
                                onChange: handleFileUpload,
                                className: "block w-full text-gray-700 border border-gray-300 rounded-lg p-2 focus:ring focus:ring-blue-200 focus:outline-none"
                            }, void 0, false, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 267,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                value: modelType,
                                onChange: (e)=>setModelType(e.target.value),
                                className: "block w-full text-gray-700 border border-gray-300 rounded-lg p-2 focus:ring focus:ring-blue-200 focus:outline-none",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                        value: "knn",
                                        children: "KNN"
                                    }, void 0, false, {
                                        fileName: "[project]/app/page.js",
                                        lineNumber: 278,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                        value: "logistic_regression",
                                        children: "Logistic Regression"
                                    }, void 0, false, {
                                        fileName: "[project]/app/page.js",
                                        lineNumber: 279,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                        value: "random_forest",
                                        children: "Random Forest"
                                    }, void 0, false, {
                                        fileName: "[project]/app/page.js",
                                        lineNumber: 280,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                        value: "decision_tree",
                                        children: "Decision Tree"
                                    }, void 0, false, {
                                        fileName: "[project]/app/page.js",
                                        lineNumber: 281,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 273,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "submit",
                                className: `w-full rounded-lg py-2 font-semibold transition ${isTraining ? "bg-gray-500 cursor-not-allowed" : "bg-blue-600 text-white hover:bg-blue-700 cursor-pointer"}`,
                                disabled: isTraining,
                                children: isTraining ? "Training..." : "Train"
                            }, void 0, false, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 283,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 266,
                        columnNumber: 9
                    }, this),
                    trainResult && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "mt-4 text-green-600 font-semibold",
                        children: trainResult
                    }, void 0, false, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 296,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/page.js",
                lineNumber: 262,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "bg-white shadow-lg rounded-lg p-6 w-full max-w-md mt-6",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                        className: "text-xl font-semibold text-gray-700 mb-4",
                        children: "Make a Prediction"
                    }, void 0, false, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 302,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "space-y-4",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                value: selectedModelType,
                                onChange: (e)=>setSelectedModelType(e.target.value),
                                className: "block w-full text-gray-700 border border-gray-300 rounded-lg p-2 focus:ring focus:ring-blue-200 focus:outline-none",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                        value: "",
                                        disabled: true,
                                        children: "Select a trained model"
                                    }, void 0, false, {
                                        fileName: "[project]/app/page.js",
                                        lineNumber: 311,
                                        columnNumber: 13
                                    }, this),
                                    Object.keys(trainedModels).map((modelType)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                            value: modelType,
                                            children: modelType.replace(/_/g, " ").toUpperCase()
                                        }, modelType, false, {
                                            fileName: "[project]/app/page.js",
                                            lineNumber: 315,
                                            columnNumber: 15
                                        }, this))
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 306,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("textarea", {
                                value: inputText,
                                onChange: (e)=>setInputText(e.target.value),
                                placeholder: "Enter text to classify...",
                                className: "block w-full text-gray-700 border border-gray-300 rounded-lg p-2 h-32 focus:ring focus:ring-blue-200 focus:outline-none"
                            }, void 0, false, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 321,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                onClick: handlePredict,
                                disabled: !selectedModelType || !trainedModels[selectedModelType],
                                className: `w-full rounded-lg py-2 font-semibold transition ${!selectedModelType ? "bg-gray-500 cursor-not-allowed" : "bg-blue-600 text-white hover:bg-blue-700 cursor-pointer"}`,
                                children: "Predict"
                            }, void 0, false, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 328,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 305,
                        columnNumber: 9
                    }, this),
                    prediction && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "mt-4",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                className: "font-semibold text-gray-700",
                                children: "Prediction Result:"
                            }, void 0, false, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 342,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: `p-3 mt-2 rounded-lg font-bold text-center ${prediction === "real" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`,
                                children: prediction.toUpperCase()
                            }, void 0, false, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 343,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 341,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/page.js",
                lineNumber: 301,
                columnNumber: 7
            }, this),
            evaluationMetrics && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "bg-white shadow-lg rounded-lg p-6 w-full max-w-md mt-6",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                        className: "text-xl font-semibold text-gray-700 mb-4",
                        children: "Model Evaluation Metrics"
                    }, void 0, false, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 359,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("table", {
                        className: "w-full border-collapse border border-gray-300",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("thead", {
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                    className: "bg-gray-200",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                            className: "border border-gray-300 p-2 text-left",
                                            children: "Metric"
                                        }, void 0, false, {
                                            fileName: "[project]/app/page.js",
                                            lineNumber: 365,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                            className: "border border-gray-300 p-2 text-left",
                                            children: "Value"
                                        }, void 0, false, {
                                            fileName: "[project]/app/page.js",
                                            lineNumber: 366,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/app/page.js",
                                    lineNumber: 364,
                                    columnNumber: 15
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 363,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tbody", {
                                children: Object.entries(evaluationMetrics).map(([key, value])=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                        className: "odd:bg-white even:bg-gray-100",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                className: "border border-gray-300 p-2",
                                                children: key
                                            }, void 0, false, {
                                                fileName: "[project]/app/page.js",
                                                lineNumber: 372,
                                                columnNumber: 19
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                className: "border border-gray-300 p-2 font-semibold",
                                                children: typeof value === "number" ? value.toFixed(4) : value
                                            }, void 0, false, {
                                                fileName: "[project]/app/page.js",
                                                lineNumber: 373,
                                                columnNumber: 19
                                            }, this)
                                        ]
                                    }, key, true, {
                                        fileName: "[project]/app/page.js",
                                        lineNumber: 371,
                                        columnNumber: 17
                                    }, this))
                            }, void 0, false, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 369,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 362,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/page.js",
                lineNumber: 358,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/page.js",
        lineNumber: 260,
        columnNumber: 5
    }, this);
}
_s(Home, "l7VbXmKNOs6TdIaJm8UFc2FK1qE=");
_c = Home;
var _c;
__turbopack_context__.k.register(_c, "Home");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
}]);

//# sourceMappingURL=app_page_00bddc8e.js.map