// utils/tfidf.js
export class TFIDF {
  constructor() {
    this.documents = [];
    this.termFreqs = [];
    this.idfScores = {};
  }

  tokenize(text) {
    return text.toLowerCase().match(/\b\w+\b/g) || [];
  }

  computeTF(words) {
    const tf = {};
    words.forEach((word) => {
      tf[word] = (tf[word] || 0) + 1;
    });
    const totalWords = words.length;
    Object.keys(tf).forEach((word) => {
      tf[word] /= totalWords;
    });
    return tf;
  }

  computeIDF() {
    const totalDocs = this.documents.length;
    const docFrequency = {};

    this.documents.forEach((words) => {
      const uniqueWords = new Set(words);
      uniqueWords.forEach((word) => {
        docFrequency[word] = (docFrequency[word] || 0) + 1;
      });
    });

    Object.keys(docFrequency).forEach((word) => {
      this.idfScores[word] = Math.log(totalDocs / (docFrequency[word] + 1));
    });
  }

  fit(documents) {
    this.documents = documents.map(this.tokenize);
    this.termFreqs = this.documents.map((doc) => this.computeTF(doc));
    this.computeIDF();
  }

  transform(text) {
    const words = this.tokenize(text);
    const tf = this.computeTF(words);
    const tfidfVector = {};

    Object.keys(tf).forEach((word) => {
      if (this.idfScores[word] !== undefined) {
        tfidfVector[word] = tf[word] * this.idfScores[word];
      }
    });

    return Object.values(tfidfVector);
  }
}
