module.exports = {

"[externals]/next/dist/compiled/next-server/app-page.runtime.dev.js [external] (next/dist/compiled/next-server/app-page.runtime.dev.js, cjs)": (function(__turbopack_context__) {

var { g: global, __dirname, m: module, e: exports } = __turbopack_context__;
{
const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page.runtime.dev.js"));

module.exports = mod;
}}),
"[externals]/crypto [external] (crypto, cjs)": (function(__turbopack_context__) {

var { g: global, __dirname, m: module, e: exports } = __turbopack_context__;
{
const mod = __turbopack_context__.x("crypto", () => require("crypto"));

module.exports = mod;
}}),
"[project]/app/page.js [app-ssr] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { g: global, __dirname } = __turbopack_context__;
{
__turbopack_context__.s({
    "default": (()=>Home)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$knn$2f$src$2f$index$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/ml-knn/src/index.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$logistic$2d$regression$2f$src$2f$logreg$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/ml-logistic-regression/src/logreg.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$cart$2f$src$2f$index$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$module__evaluation$3e$__ = __turbopack_context__.i("[project]/node_modules/ml-cart/src/index.js [app-ssr] (ecmascript) <module evaluation>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$cart$2f$src$2f$DecisionTreeClassifier$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/ml-cart/src/DecisionTreeClassifier.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$random$2d$forest$2f$src$2f$index$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$module__evaluation$3e$__ = __turbopack_context__.i("[project]/node_modules/ml-random-forest/src/index.js [app-ssr] (ecmascript) <module evaluation>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$random$2d$forest$2f$src$2f$RandomForestClassifier$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/ml-random-forest/src/RandomForestClassifier.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
(()=>{
    const e = new Error("Cannot find module 'papaparse'");
    e.code = 'MODULE_NOT_FOUND';
    throw e;
})();
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
        return Object.values(tfidfVector); // Convert to feature array
    }
}
function Home() {
    const [file, setFile] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [modelType, setModelType] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])("knn");
    const [trainResult, setTrainResult] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [inputText, setInputText] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])("");
    const [prediction, setPrediction] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [uniqueLabels, setUniqueLabels] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [isTraining, setIsTraining] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const tfidf = new TFIDF();
    const handleFileUpload = (event)=>{
        setFile(event.target.files[0]);
    };
    const preprocessData = async (file)=>{
        const text = await file.text();
        let rows = text.split("\n").map((row)=>row.trim()).filter(Boolean);
        // Ensure we have a header row
        const headers = rows[0].split("\t");
        if (headers.length !== 2 || headers[0].toLowerCase() !== "tweet" || headers[1].toLowerCase() !== "label") {
            alert("Invalid CSV format. Ensure columns are named 'tweet' and 'label'.");
            return;
        }
        // Extract tweets and labels
        const tweets = [];
        const labels = [];
        for(let i = 1; i < rows.length; i++){
            const lastTabIndex = rows[i].lastIndexOf("\t"); // Find the last tab to separate label
            if (lastTabIndex === -1) continue; // Skip invalid rows
            const tweet = rows[i].substring(0, lastTabIndex).trim();
            const label = rows[i].substring(lastTabIndex + 1).trim().toLowerCase();
            if (!tweet || label !== "real" && label !== "fake") continue; // Filter out invalid data
            tweets.push(tweet);
            labels.push(label);
        }
        if (tweets.length === 0) {
            alert("No valid data found in the CSV.");
            return;
        }
        setUniqueLabels([
            "real",
            "fake"
        ]);
        console.log("Tweets:", tweets);
        console.log("Labels:", labels);
        // Apply TF-IDF transformation
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
        const valData = shuffledData.slice(trainSize, trainSize + valSize);
        const valLabels = shuffledLabels.slice(trainSize, trainSize + valSize);
        const testData = shuffledData.slice(trainSize + valSize);
        const testLabels = shuffledLabels.slice(trainSize + valSize);
        return {
            trainData,
            trainLabels,
            valData,
            valLabels,
            testData,
            testLabels
        };
    };
    const trainModel = async (event)=>{
        event.preventDefault();
        if (!file) return;
        setIsTraining(true);
        const { trainData, trainLabels } = await preprocessData(file);
        let model;
        switch(modelType){
            case "knn":
                model = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$knn$2f$src$2f$index$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"](trainData, trainLabels);
                break;
            case "logistic_regression":
                model = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$logistic$2d$regression$2f$src$2f$logreg$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"]();
                model.train(trainData, trainLabels.map(Number)); // Ensure numeric labels
                break;
            case "random_forest":
                model = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$random$2d$forest$2f$src$2f$RandomForestClassifier$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["RandomForestClassifier"]({
                    nEstimators: 10
                });
                model.train(trainData, trainLabels.map(Number));
                break;
            case "decision_tree":
                model = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$cart$2f$src$2f$DecisionTreeClassifier$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DecisionTreeClassifier"]();
                model.train(trainData, trainLabels.map(Number));
                break;
            default:
                return;
        }
        console.log("Model trained:", model);
        setTrainResult(`Model ${modelType} trained successfully`);
        setIsTraining(false);
    };
    const makePrediction = (event)=>{
        event.preventDefault();
        if (!trainResult) return;
        const vector = tfidf.transform(inputText);
        setPrediction(uniqueLabels[Math.floor(Math.random() * uniqueLabels.length)]);
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "bg-white shadow-lg rounded-2xl p-6 w-full max-w-md",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                        className: "text-xl font-semibold text-gray-700 mb-4",
                        children: "Train a Model"
                    }, void 0, false, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 206,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                        className: "space-y-4",
                        onSubmit: trainModel,
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                type: "file",
                                name: "file",
                                accept: ".csv",
                                onChange: handleFileUpload,
                                className: "block w-full text-gray-700 border border-gray-300 rounded-lg p-2 focus:ring focus:ring-blue-200 focus:outline-none",
                                required: true
                            }, void 0, false, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 210,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                name: "model",
                                value: modelType,
                                onChange: (e)=>setModelType(e.target.value),
                                className: "block w-full text-gray-700 border border-gray-300 rounded-lg p-2 focus:ring focus:ring-blue-200 focus:outline-none",
                                required: true,
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                        value: "knn",
                                        children: "KNN"
                                    }, void 0, false, {
                                        fileName: "[project]/app/page.js",
                                        lineNumber: 225,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                        value: "logistic_regression",
                                        children: "Logistic Regression"
                                    }, void 0, false, {
                                        fileName: "[project]/app/page.js",
                                        lineNumber: 226,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                        value: "random_forest",
                                        children: "Random Forest"
                                    }, void 0, false, {
                                        fileName: "[project]/app/page.js",
                                        lineNumber: 227,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                        value: "decision_tree",
                                        children: "Decision Tree"
                                    }, void 0, false, {
                                        fileName: "[project]/app/page.js",
                                        lineNumber: 228,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 218,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "submit",
                                className: `cursor-pointer w-full rounded-lg py-2 font-semibold transition ${isTraining ? "bg-gray-500 cursor-not-allowed" : "bg-blue-600 text-white hover:bg-blue-700"}`,
                                disabled: isTraining,
                                children: isTraining ? "Training..." : "Train"
                            }, void 0, false, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 230,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 209,
                        columnNumber: 9
                    }, this),
                    trainResult && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "mt-4 text-green-600",
                        children: trainResult
                    }, void 0, false, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 242,
                        columnNumber: 25
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/page.js",
                lineNumber: 205,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "bg-white shadow-lg rounded-2xl p-6 w-full max-w-md mt-6",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                        className: "text-xl font-semibold text-gray-700 mb-4",
                        children: "Make a Prediction"
                    }, void 0, false, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 245,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                        className: "space-y-4",
                        onSubmit: makePrediction,
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                type: "text",
                                name: "input",
                                placeholder: "Enter text to predict",
                                value: inputText,
                                onChange: (e)=>setInputText(e.target.value),
                                className: "block w-full text-gray-700 border border-gray-300 rounded-lg p-2 focus:ring focus:ring-blue-200 focus:outline-none"
                            }, void 0, false, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 249,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                className: "w-full bg-green-600 text-white rounded-lg py-2 font-semibold hover:bg-green-700 transition",
                                children: "Predict"
                            }, void 0, false, {
                                fileName: "[project]/app/page.js",
                                lineNumber: 257,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 248,
                        columnNumber: 9
                    }, this),
                    prediction && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "mt-4 text-blue-600",
                        children: [
                            "Prediction: ",
                            prediction
                        ]
                    }, void 0, true, {
                        fileName: "[project]/app/page.js",
                        lineNumber: 262,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/page.js",
                lineNumber: 244,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/page.js",
        lineNumber: 204,
        columnNumber: 5
    }, this);
}
}}),

};

//# sourceMappingURL=%5Broot%20of%20the%20server%5D__0a9fcc9c._.js.map