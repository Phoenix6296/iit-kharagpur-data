(globalThis.TURBOPACK = globalThis.TURBOPACK || []).push(["static/chunks/_b4f1c3bb._.js", {

"[project]/app/page.js [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { g: global, __dirname, k: __turbopack_refresh__, m: module } = __turbopack_context__;
{
__turbopack_context__.s({
    "default": (()=>Home)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$knn$2f$src$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/ml-knn/src/index.js [app-client] (ecmascript)");
// import LogisticRegression from "ml-logistic-regression";
// import { DecisionTreeClassifier } from "ml-cart";
// import { RandomForestClassifier } from "ml-random-forest";
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
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
        console.debug("Computing IDF");
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
        console.debug("Fitting TF-IDF model");
        this.documents = documents.map(this.tokenize);
        this.termFreqs = this.documents.map((doc)=>this.computeTF(doc));
        this.computeIDF();
    }
    transform(text) {
        console.debug("Transforming input text", text);
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
    const [inputText, setInputText] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [prediction, setPrediction] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [uniqueLabels, setUniqueLabels] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [isTraining, setIsTraining] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const tfidf = new TFIDF();
    const handleFileUpload = (event)=>{
        console.debug("File selected", event.target.files[0]);
        setFile(event.target.files[0]);
    };
    const preprocessData = async (file)=>{
        console.debug("Preprocessing file", file.name);
        const text = await file.text();
        let rows = text.split("\n").map((row)=>row.split(","));
        // Ensure each row has at least two columns (data + label)
        rows = rows.filter((row)=>row.length >= 2);
        // Extract labels (last column) and data (rest of the row)
        let labels = rows.map((row)=>row.pop()?.trim()).filter((label)=>label !== "" && label !== undefined);
        // let labels = rows.map((row) => row.pop().trim().toLowerCase()); // Normalize labels
        let data = rows.map((row)=>row.join(" ")); // Join rest as text
        // Filter out incorrect labels
        const validLabels = [
            "real",
            "fake"
        ];
        const filteredIndices = labels.map((label, index)=>validLabels.includes(label) ? index : -1).filter((index)=>index !== -1);
        // Apply filtering
        labels = filteredIndices.map((i)=>labels[i]);
        data = filteredIndices.map((i)=>data[i]);
        setUniqueLabels([
            ...new Set(labels)
        ]);
        // console.log("Final Labels:", labels);
        // console.log("Final Data:", data);
        tfidf.fit(data);
        const transformedData = data.map((text)=>tfidf.transform(text));
        // Shuffle data
        const shuffledIndices = [
            ...Array(transformedData.length).keys()
        ].sort(()=>Math.random() - 0.5);
        const shuffledData = shuffledIndices.map((i)=>transformedData[i]);
        const shuffledLabels = shuffledIndices.map((i)=>labels[i]);
        // Count the classes
        const classCounts = {
            real: 0,
            fake: 0
        };
        shuffledLabels.forEach((label)=>{
            classCounts[label]++;
        });
        // console.log("Class counts:", classCounts);
        // console.log("Shuffled data:", shuffledData);
        // console.log("Shuffled labels:", shuffledLabels);
        // console.log("TF-IDF scores:", tfidf.idfScores);
        return {
            trainData: shuffledData,
            trainLabels: shuffledLabels
        };
    };
    const trainModel = async (event)=>{
        event.preventDefault();
        if (!file) return;
        setIsTraining(true);
        console.debug("Training model type", modelType);
        const { trainData, trainLabels } = await preprocessData(file);
        let model;
        switch(modelType){
            case "knn":
                model = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$knn$2f$src$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"](trainData, trainLabels);
                break;
                // case "logistic_regression":
                //   console.debug("Formatted Data:", trainData);
                //   console.debug("Formatted Labels:", numericLabels);
                //   model = new LogisticRegression();
                //   const formattedLabels = new Matrix(
                //     trainLabels.map((label) => [Number(label)])
                //   );
                //   console.log("Formatted labels:", formattedLabels);
                //   const numericLabels = trainLabels.map((label) => {
                //     const num = Number(label);
                //     return isNaN(num) ? 0 : num;
                //   });
                //   model.train(trainData, numericLabels);
                //   break;
                // case "random_forest":
                //   model = new RandomForestClassifier({ nEstimators: 10 });
                //   model.train(trainData, trainLabels.map(Number));
                //   break;
                // case "decision_tree":
                model = new DecisionTreeClassifier();
                model.train(trainData, trainLabels.map(Number));
                break;
            default:
                return;
        }
        console.debug("Model trained successfully", model);
        setTrainResult(`Model ${modelType} trained successfully`);
        setIsTraining(false);
    };
    const makePrediction = (event)=>{
        event.preventDefault();
        if (!trainResult) return;
        console.debug("Making prediction for input", inputText);
        const vector = tfidf.transform(inputText);
        setPrediction(uniqueLabels[Math.floor(Math.random() * uniqueLabels.length)]);
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "bg-white shadow-lg rounded-2xl p-6 w-full max-w-md",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                    className: "text-xl font-semibold text-gray-700 mb-4",
                    children: "Train a Model"
                }, void 0, false, {
                    fileName: "[project]/app/page.js",
                    lineNumber: 204,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                    className: "space-y-4",
                    onSubmit: trainModel,
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                            type: "file",
                            name: "file",
                            accept: ".csv",
                            onChange: handleFileUpload,
                            required: true
                        }, void 0, false, {
                            fileName: "[project]/app/page.js",
                            lineNumber: 208,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                            name: "model",
                            value: modelType,
                            onChange: (e)=>setModelType(e.target.value),
                            required: true,
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                    value: "knn",
                                    children: "KNN"
                                }, void 0, false, {
                                    fileName: "[project]/app/page.js",
                                    lineNumber: 221,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                    value: "logistic_regression",
                                    children: "Logistic Regression"
                                }, void 0, false, {
                                    fileName: "[project]/app/page.js",
                                    lineNumber: 222,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                    value: "random_forest",
                                    children: "Random Forest"
                                }, void 0, false, {
                                    fileName: "[project]/app/page.js",
                                    lineNumber: 223,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                    value: "decision_tree",
                                    children: "Decision Tree"
                                }, void 0, false, {
                                    fileName: "[project]/app/page.js",
                                    lineNumber: 224,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/app/page.js",
                            lineNumber: 215,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "submit",
                            disabled: isTraining,
                            children: isTraining ? "Training..." : "Train"
                        }, void 0, false, {
                            fileName: "[project]/app/page.js",
                            lineNumber: 226,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/app/page.js",
                    lineNumber: 207,
                    columnNumber: 9
                }, this),
                trainResult && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    children: trainResult
                }, void 0, false, {
                    fileName: "[project]/app/page.js",
                    lineNumber: 230,
                    columnNumber: 25
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/app/page.js",
            lineNumber: 203,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/app/page.js",
        lineNumber: 202,
        columnNumber: 5
    }, this);
}
_s(Home, "+5xBvVN77Vuncn8UjDN+sv70LTk=");
_c = Home;
var _c;
__turbopack_context__.k.register(_c, "Home");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(module, globalThis.$RefreshHelpers$);
}
}}),
"[project]/node_modules/next/dist/compiled/react/cjs/react-jsx-dev-runtime.development.js [app-client] (ecmascript)": (function(__turbopack_context__) {

var { g: global, __dirname, m: module, e: exports } = __turbopack_context__;
{
/**
 * @license React
 * react-jsx-dev-runtime.development.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */ var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
"use strict";
"production" !== ("TURBOPACK compile-time value", "development") && function() {
    function getComponentNameFromType(type) {
        if (null == type) return null;
        if ("function" === typeof type) return type.$$typeof === REACT_CLIENT_REFERENCE ? null : type.displayName || type.name || null;
        if ("string" === typeof type) return type;
        switch(type){
            case REACT_FRAGMENT_TYPE:
                return "Fragment";
            case REACT_PORTAL_TYPE:
                return "Portal";
            case REACT_PROFILER_TYPE:
                return "Profiler";
            case REACT_STRICT_MODE_TYPE:
                return "StrictMode";
            case REACT_SUSPENSE_TYPE:
                return "Suspense";
            case REACT_SUSPENSE_LIST_TYPE:
                return "SuspenseList";
        }
        if ("object" === typeof type) switch("number" === typeof type.tag && console.error("Received an unexpected object in getComponentNameFromType(). This is likely a bug in React. Please file an issue."), type.$$typeof){
            case REACT_CONTEXT_TYPE:
                return (type.displayName || "Context") + ".Provider";
            case REACT_CONSUMER_TYPE:
                return (type._context.displayName || "Context") + ".Consumer";
            case REACT_FORWARD_REF_TYPE:
                var innerType = type.render;
                type = type.displayName;
                type || (type = innerType.displayName || innerType.name || "", type = "" !== type ? "ForwardRef(" + type + ")" : "ForwardRef");
                return type;
            case REACT_MEMO_TYPE:
                return innerType = type.displayName || null, null !== innerType ? innerType : getComponentNameFromType(type.type) || "Memo";
            case REACT_LAZY_TYPE:
                innerType = type._payload;
                type = type._init;
                try {
                    return getComponentNameFromType(type(innerType));
                } catch (x) {}
        }
        return null;
    }
    function testStringCoercion(value) {
        return "" + value;
    }
    function checkKeyStringCoercion(value) {
        try {
            testStringCoercion(value);
            var JSCompiler_inline_result = !1;
        } catch (e) {
            JSCompiler_inline_result = !0;
        }
        if (JSCompiler_inline_result) {
            JSCompiler_inline_result = console;
            var JSCompiler_temp_const = JSCompiler_inline_result.error;
            var JSCompiler_inline_result$jscomp$0 = "function" === typeof Symbol && Symbol.toStringTag && value[Symbol.toStringTag] || value.constructor.name || "Object";
            JSCompiler_temp_const.call(JSCompiler_inline_result, "The provided key is an unsupported type %s. This value must be coerced to a string before using it here.", JSCompiler_inline_result$jscomp$0);
            return testStringCoercion(value);
        }
    }
    function getTaskName(type) {
        if (type === REACT_FRAGMENT_TYPE) return "<>";
        if ("object" === typeof type && null !== type && type.$$typeof === REACT_LAZY_TYPE) return "<...>";
        try {
            var name = getComponentNameFromType(type);
            return name ? "<" + name + ">" : "<...>";
        } catch (x) {
            return "<...>";
        }
    }
    function getOwner() {
        var dispatcher = ReactSharedInternals.A;
        return null === dispatcher ? null : dispatcher.getOwner();
    }
    function hasValidKey(config) {
        if (hasOwnProperty.call(config, "key")) {
            var getter = Object.getOwnPropertyDescriptor(config, "key").get;
            if (getter && getter.isReactWarning) return !1;
        }
        return void 0 !== config.key;
    }
    function defineKeyPropWarningGetter(props, displayName) {
        function warnAboutAccessingKey() {
            specialPropKeyWarningShown || (specialPropKeyWarningShown = !0, console.error("%s: `key` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://react.dev/link/special-props)", displayName));
        }
        warnAboutAccessingKey.isReactWarning = !0;
        Object.defineProperty(props, "key", {
            get: warnAboutAccessingKey,
            configurable: !0
        });
    }
    function elementRefGetterWithDeprecationWarning() {
        var componentName = getComponentNameFromType(this.type);
        didWarnAboutElementRef[componentName] || (didWarnAboutElementRef[componentName] = !0, console.error("Accessing element.ref was removed in React 19. ref is now a regular prop. It will be removed from the JSX Element type in a future release."));
        componentName = this.props.ref;
        return void 0 !== componentName ? componentName : null;
    }
    function ReactElement(type, key, self, source, owner, props, debugStack, debugTask) {
        self = props.ref;
        type = {
            $$typeof: REACT_ELEMENT_TYPE,
            type: type,
            key: key,
            props: props,
            _owner: owner
        };
        null !== (void 0 !== self ? self : null) ? Object.defineProperty(type, "ref", {
            enumerable: !1,
            get: elementRefGetterWithDeprecationWarning
        }) : Object.defineProperty(type, "ref", {
            enumerable: !1,
            value: null
        });
        type._store = {};
        Object.defineProperty(type._store, "validated", {
            configurable: !1,
            enumerable: !1,
            writable: !0,
            value: 0
        });
        Object.defineProperty(type, "_debugInfo", {
            configurable: !1,
            enumerable: !1,
            writable: !0,
            value: null
        });
        Object.defineProperty(type, "_debugStack", {
            configurable: !1,
            enumerable: !1,
            writable: !0,
            value: debugStack
        });
        Object.defineProperty(type, "_debugTask", {
            configurable: !1,
            enumerable: !1,
            writable: !0,
            value: debugTask
        });
        Object.freeze && (Object.freeze(type.props), Object.freeze(type));
        return type;
    }
    function jsxDEVImpl(type, config, maybeKey, isStaticChildren, source, self, debugStack, debugTask) {
        var children = config.children;
        if (void 0 !== children) if (isStaticChildren) if (isArrayImpl(children)) {
            for(isStaticChildren = 0; isStaticChildren < children.length; isStaticChildren++)validateChildKeys(children[isStaticChildren]);
            Object.freeze && Object.freeze(children);
        } else console.error("React.jsx: Static children should always be an array. You are likely explicitly calling React.jsxs or React.jsxDEV. Use the Babel transform instead.");
        else validateChildKeys(children);
        if (hasOwnProperty.call(config, "key")) {
            children = getComponentNameFromType(type);
            var keys = Object.keys(config).filter(function(k) {
                return "key" !== k;
            });
            isStaticChildren = 0 < keys.length ? "{key: someKey, " + keys.join(": ..., ") + ": ...}" : "{key: someKey}";
            didWarnAboutKeySpread[children + isStaticChildren] || (keys = 0 < keys.length ? "{" + keys.join(": ..., ") + ": ...}" : "{}", console.error('A props object containing a "key" prop is being spread into JSX:\n  let props = %s;\n  <%s {...props} />\nReact keys must be passed directly to JSX without using spread:\n  let props = %s;\n  <%s key={someKey} {...props} />', isStaticChildren, children, keys, children), didWarnAboutKeySpread[children + isStaticChildren] = !0);
        }
        children = null;
        void 0 !== maybeKey && (checkKeyStringCoercion(maybeKey), children = "" + maybeKey);
        hasValidKey(config) && (checkKeyStringCoercion(config.key), children = "" + config.key);
        if ("key" in config) {
            maybeKey = {};
            for(var propName in config)"key" !== propName && (maybeKey[propName] = config[propName]);
        } else maybeKey = config;
        children && defineKeyPropWarningGetter(maybeKey, "function" === typeof type ? type.displayName || type.name || "Unknown" : type);
        return ReactElement(type, children, self, source, getOwner(), maybeKey, debugStack, debugTask);
    }
    function validateChildKeys(node) {
        "object" === typeof node && null !== node && node.$$typeof === REACT_ELEMENT_TYPE && node._store && (node._store.validated = 1);
    }
    var React = __turbopack_context__.r("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)"), REACT_ELEMENT_TYPE = Symbol.for("react.transitional.element"), REACT_PORTAL_TYPE = Symbol.for("react.portal"), REACT_FRAGMENT_TYPE = Symbol.for("react.fragment"), REACT_STRICT_MODE_TYPE = Symbol.for("react.strict_mode"), REACT_PROFILER_TYPE = Symbol.for("react.profiler");
    Symbol.for("react.provider");
    var REACT_CONSUMER_TYPE = Symbol.for("react.consumer"), REACT_CONTEXT_TYPE = Symbol.for("react.context"), REACT_FORWARD_REF_TYPE = Symbol.for("react.forward_ref"), REACT_SUSPENSE_TYPE = Symbol.for("react.suspense"), REACT_SUSPENSE_LIST_TYPE = Symbol.for("react.suspense_list"), REACT_MEMO_TYPE = Symbol.for("react.memo"), REACT_LAZY_TYPE = Symbol.for("react.lazy"), REACT_CLIENT_REFERENCE = Symbol.for("react.client.reference"), ReactSharedInternals = React.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE, hasOwnProperty = Object.prototype.hasOwnProperty, isArrayImpl = Array.isArray, createTask = console.createTask ? console.createTask : function() {
        return null;
    }, specialPropKeyWarningShown;
    var didWarnAboutElementRef = {};
    var didWarnAboutKeySpread = {};
    exports.Fragment = REACT_FRAGMENT_TYPE;
    exports.jsxDEV = function(type, config, maybeKey, isStaticChildren, source, self) {
        return jsxDEVImpl(type, config, maybeKey, isStaticChildren, source, self, Error("react-stack-top-frame"), createTask(getTaskName(type)));
    };
}();
}}),
"[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)": (function(__turbopack_context__) {

var { g: global, __dirname, m: module, e: exports } = __turbopack_context__;
{
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
'use strict';
if ("TURBOPACK compile-time falsy", 0) {
    "TURBOPACK unreachable";
} else {
    module.exports = __turbopack_context__.r("[project]/node_modules/next/dist/compiled/react/cjs/react-jsx-dev-runtime.development.js [app-client] (ecmascript)");
}
}}),
"[project]/node_modules/ml-distance-euclidean/lib-es6/euclidean.js [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { g: global, __dirname } = __turbopack_context__;
{
__turbopack_context__.s({
    "euclidean": (()=>euclidean),
    "squaredEuclidean": (()=>squaredEuclidean)
});
function squaredEuclidean(p, q) {
    let d = 0;
    for(let i = 0; i < p.length; i++){
        d += (p[i] - q[i]) * (p[i] - q[i]);
    }
    return d;
}
function euclidean(p, q) {
    return Math.sqrt(squaredEuclidean(p, q));
}
}}),
"[project]/node_modules/ml-knn/src/KDTree.js [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { g: global, __dirname } = __turbopack_context__;
{
/*
 * Original code from:
 *
 * k-d Tree JavaScript - V 1.01
 *
 * https://github.com/ubilabs/kd-tree-javascript
 *
 * @author Mircea Pricop <pricop@ubilabs.net>, 2012
 * @author Martin Kleppe <kleppe@ubilabs.net>, 2012
 * @author Ubilabs http://ubilabs.net, 2012
 * @license MIT License <http://www.opensource.org/licenses/mit-license.php>
 */ __turbopack_context__.s({
    "default": (()=>KDTree)
});
function Node(obj, dimension, parent) {
    this.obj = obj;
    this.left = null;
    this.right = null;
    this.parent = parent;
    this.dimension = dimension;
}
class KDTree {
    constructor(points, metric){
        // If points is not an array, assume we're loading a pre-built tree
        if (!Array.isArray(points)) {
            this.dimensions = points.dimensions;
            this.root = points;
            restoreParent(this.root);
        } else {
            this.dimensions = new Array(points[0].length);
            for(var i = 0; i < this.dimensions.length; i++){
                this.dimensions[i] = i;
            }
            this.root = buildTree(points, 0, null, this.dimensions);
        }
        this.metric = metric;
    }
    // Convert to a JSON serializable structure; this just requires removing
    // the `parent` property
    toJSON() {
        const result = toJSONImpl(this.root, true);
        result.dimensions = this.dimensions;
        return result;
    }
    nearest(point, maxNodes, maxDistance) {
        const metric = this.metric;
        const dimensions = this.dimensions;
        var i;
        const bestNodes = new BinaryHeap(function(e) {
            return -e[1];
        });
        function nearestSearch(node) {
            const dimension = dimensions[node.dimension];
            const ownDistance = metric(point, node.obj);
            const linearPoint = {};
            var bestChild, linearDistance, otherChild, i;
            function saveNode(node, distance) {
                bestNodes.push([
                    node,
                    distance
                ]);
                if (bestNodes.size() > maxNodes) {
                    bestNodes.pop();
                }
            }
            for(i = 0; i < dimensions.length; i += 1){
                if (i === node.dimension) {
                    linearPoint[dimensions[i]] = point[dimensions[i]];
                } else {
                    linearPoint[dimensions[i]] = node.obj[dimensions[i]];
                }
            }
            linearDistance = metric(linearPoint, node.obj);
            if (node.right === null && node.left === null) {
                if (bestNodes.size() < maxNodes || ownDistance < bestNodes.peek()[1]) {
                    saveNode(node, ownDistance);
                }
                return;
            }
            if (node.right === null) {
                bestChild = node.left;
            } else if (node.left === null) {
                bestChild = node.right;
            } else {
                if (point[dimension] < node.obj[dimension]) {
                    bestChild = node.left;
                } else {
                    bestChild = node.right;
                }
            }
            nearestSearch(bestChild);
            if (bestNodes.size() < maxNodes || ownDistance < bestNodes.peek()[1]) {
                saveNode(node, ownDistance);
            }
            if (bestNodes.size() < maxNodes || Math.abs(linearDistance) < bestNodes.peek()[1]) {
                if (bestChild === node.left) {
                    otherChild = node.right;
                } else {
                    otherChild = node.left;
                }
                if (otherChild !== null) {
                    nearestSearch(otherChild);
                }
            }
        }
        if (maxDistance) {
            for(i = 0; i < maxNodes; i += 1){
                bestNodes.push([
                    null,
                    maxDistance
                ]);
            }
        }
        if (this.root) {
            nearestSearch(this.root);
        }
        const result = [];
        for(i = 0; i < Math.min(maxNodes, bestNodes.content.length); i += 1){
            if (bestNodes.content[i][0]) {
                result.push([
                    bestNodes.content[i][0].obj,
                    bestNodes.content[i][1]
                ]);
            }
        }
        return result;
    }
}
function toJSONImpl(src) {
    const dest = new Node(src.obj, src.dimension, null);
    if (src.left) dest.left = toJSONImpl(src.left);
    if (src.right) dest.right = toJSONImpl(src.right);
    return dest;
}
function buildTree(points, depth, parent, dimensions) {
    const dim = depth % dimensions.length;
    if (points.length === 0) {
        return null;
    }
    if (points.length === 1) {
        return new Node(points[0], dim, parent);
    }
    points.sort((a, b)=>a[dimensions[dim]] - b[dimensions[dim]]);
    const median = Math.floor(points.length / 2);
    const node = new Node(points[median], dim, parent);
    node.left = buildTree(points.slice(0, median), depth + 1, node, dimensions);
    node.right = buildTree(points.slice(median + 1), depth + 1, node, dimensions);
    return node;
}
function restoreParent(root) {
    if (root.left) {
        root.left.parent = root;
        restoreParent(root.left);
    }
    if (root.right) {
        root.right.parent = root;
        restoreParent(root.right);
    }
}
// Binary heap implementation from:
// http://eloquentjavascript.net/appendix2.html
class BinaryHeap {
    constructor(scoreFunction){
        this.content = [];
        this.scoreFunction = scoreFunction;
    }
    push(element) {
        // Add the new element to the end of the array.
        this.content.push(element);
        // Allow it to bubble up.
        this.bubbleUp(this.content.length - 1);
    }
    pop() {
        // Store the first element so we can return it later.
        var result = this.content[0];
        // Get the element at the end of the array.
        var end = this.content.pop();
        // If there are any elements left, put the end element at the
        // start, and let it sink down.
        if (this.content.length > 0) {
            this.content[0] = end;
            this.sinkDown(0);
        }
        return result;
    }
    peek() {
        return this.content[0];
    }
    size() {
        return this.content.length;
    }
    bubbleUp(n) {
        // Fetch the element that has to be moved.
        var element = this.content[n];
        // When at 0, an element can not go up any further.
        while(n > 0){
            // Compute the parent element's index, and fetch it.
            const parentN = Math.floor((n + 1) / 2) - 1;
            const parent = this.content[parentN];
            // Swap the elements if the parent is greater.
            if (this.scoreFunction(element) < this.scoreFunction(parent)) {
                this.content[parentN] = element;
                this.content[n] = parent;
                // Update 'n' to continue at the new position.
                n = parentN;
            } else {
                break;
            }
        }
    }
    sinkDown(n) {
        // Look up the target element and its score.
        var length = this.content.length;
        var element = this.content[n];
        var elemScore = this.scoreFunction(element);
        while(true){
            // Compute the indices of the child elements.
            var child2N = (n + 1) * 2;
            var child1N = child2N - 1;
            // This is used to store the new position of the element,
            // if any.
            var swap = null;
            // If the first child exists (is inside the array)...
            if (child1N < length) {
                // Look it up and compute its score.
                var child1 = this.content[child1N];
                var child1Score = this.scoreFunction(child1);
                // If the score is less than our element's, we need to swap.
                if (child1Score < elemScore) {
                    swap = child1N;
                }
            }
            // Do the same checks for the other child.
            if (child2N < length) {
                var child2 = this.content[child2N];
                var child2Score = this.scoreFunction(child2);
                if (child2Score < (swap === null ? elemScore : child1Score)) {
                    swap = child2N;
                }
            }
            // If the element needs to be moved, swap it, and continue.
            if (swap !== null) {
                this.content[n] = this.content[swap];
                this.content[swap] = element;
                n = swap;
            } else {
                break;
            }
        }
    }
}
}}),
"[project]/node_modules/ml-knn/src/index.js [app-client] (ecmascript)": ((__turbopack_context__) => {
"use strict";

var { g: global, __dirname } = __turbopack_context__;
{
__turbopack_context__.s({
    "default": (()=>KNN)
});
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$distance$2d$euclidean$2f$lib$2d$es6$2f$euclidean$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/ml-distance-euclidean/lib-es6/euclidean.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$knn$2f$src$2f$KDTree$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/ml-knn/src/KDTree.js [app-client] (ecmascript)");
;
;
class KNN {
    /**
   * @param {Array} dataset
   * @param {Array} labels
   * @param {object} options
   * @param {number} [options.k=numberOfClasses + 1] - Number of neighbors to classify.
   * @param {function} [options.distance=euclideanDistance] - Distance function that takes two parameters.
   */ constructor(dataset, labels, options = {}){
        if (dataset === true) {
            const model = labels;
            this.kdTree = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$knn$2f$src$2f$KDTree$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"](model.kdTree, options);
            this.k = model.k;
            this.classes = new Set(model.classes);
            this.isEuclidean = model.isEuclidean;
            return;
        }
        const classes = new Set(labels);
        const { distance = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$distance$2d$euclidean$2f$lib$2d$es6$2f$euclidean$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["euclidean"], k = classes.size + 1 } = options;
        const points = new Array(dataset.length);
        for(var i = 0; i < points.length; ++i){
            points[i] = dataset[i].slice();
        }
        for(i = 0; i < labels.length; ++i){
            points[i].push(labels[i]);
        }
        this.kdTree = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$knn$2f$src$2f$KDTree$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"](points, distance);
        this.k = k;
        this.classes = classes;
        this.isEuclidean = distance === __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$distance$2d$euclidean$2f$lib$2d$es6$2f$euclidean$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["euclidean"];
    }
    /**
   * Create a new KNN instance with the given model.
   * @param {object} model
   * @param {function} distance=euclideanDistance - distance function must be provided if the model wasn't trained with euclidean distance.
   * @return {KNN}
   */ static load(model, distance = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$distance$2d$euclidean$2f$lib$2d$es6$2f$euclidean$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["euclidean"]) {
        if (model.name !== 'KNN') {
            throw new Error(`invalid model: ${model.name}`);
        }
        if (!model.isEuclidean && distance === __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$distance$2d$euclidean$2f$lib$2d$es6$2f$euclidean$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["euclidean"]) {
            throw new Error('a custom distance function was used to create the model. Please provide it again');
        }
        if (model.isEuclidean && distance !== __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$ml$2d$distance$2d$euclidean$2f$lib$2d$es6$2f$euclidean$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["euclidean"]) {
            throw new Error('the model was created with the default distance function. Do not load it with another one');
        }
        return new KNN(true, model, distance);
    }
    /**
   * Return a JSON containing the kd-tree model.
   * @return {object} JSON KNN model.
   */ toJSON() {
        return {
            name: 'KNN',
            kdTree: this.kdTree,
            k: this.k,
            classes: Array.from(this.classes),
            isEuclidean: this.isEuclidean
        };
    }
    /**
   * Predicts the output given the matrix to predict.
   * @param {Array} dataset
   * @return {Array} predictions
   */ predict(dataset) {
        if (Array.isArray(dataset)) {
            if (typeof dataset[0] === 'number') {
                return getSinglePrediction(this, dataset);
            } else if (Array.isArray(dataset[0]) && typeof dataset[0][0] === 'number') {
                const predictions = new Array(dataset.length);
                for(var i = 0; i < dataset.length; i++){
                    predictions[i] = getSinglePrediction(this, dataset[i]);
                }
                return predictions;
            }
        }
        throw new TypeError('dataset to predict must be an array or a matrix');
    }
}
function getSinglePrediction(knn, currentCase) {
    var nearestPoints = knn.kdTree.nearest(currentCase, knn.k);
    var pointsPerClass = {};
    var predictedClass = -1;
    var maxPoints = -1;
    var lastElement = nearestPoints[0][0].length - 1;
    for (var element of knn.classes){
        pointsPerClass[element] = 0;
    }
    for(var i = 0; i < nearestPoints.length; ++i){
        var currentClass = nearestPoints[i][0][lastElement];
        var currentPoints = ++pointsPerClass[currentClass];
        if (currentPoints > maxPoints) {
            predictedClass = currentClass;
            maxPoints = currentPoints;
        }
    }
    return predictedClass;
}
}}),
}]);

//# sourceMappingURL=_b4f1c3bb._.js.map