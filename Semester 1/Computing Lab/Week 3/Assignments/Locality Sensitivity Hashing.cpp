#include <iostream>
#include <random>

#define SENTENCES 10
#define SHINGLE_SIZE 3
#define VECTOR_SIZE 10
#define PERMUTATIONS 10

using namespace std;

// Please Note: Assuming the sentence is of 100 length only for because the I have taken the dp array size to be 100x100

int editDistanceHelper(string &str1, string &str2, int m, int n, int dp[][100])
{
    if (m == 0)
        return n;
    if (n == 0)
        return m;

    if (dp[m][n] != -1)
        return dp[m][n];

    if (toupper(str1[m - 1]) == toupper(str2[n - 1]))
        return dp[m][n] = editDistanceHelper(str1, str2, m - 1, n - 1, dp);

    int insert = editDistanceHelper(str1, str2, m, n - 1, dp);
    int remove = editDistanceHelper(str1, str2, m - 1, n, dp);
    int replace = editDistanceHelper(str1, str2, m - 1, n - 1, dp);

    return dp[m][n] = 1 + min(insert, min(remove, replace));
}

int editDistance(string &str1, string &str2)
{
    int m = str1.length();
    int n = str2.length();
    int dp[100][100];

    for (int i = 0; i <= m; i++)
        for (int j = 0; j <= n; j++)
            dp[i][j] = -1;

    return editDistanceHelper(str1, str2, m, n, dp);
}

int shingleExists(string *vocabulary, int vocabSize, string &shingle)
{
    for (int i = 0; i < vocabSize; i++)
        if (vocabulary[i] == shingle)
            return i;
    return -1;
}

int createVocabulary(string *sentences, string *vocabulary)
{
    int vocabSize = 0;
    for (int k = 0; k < SENTENCES; k++)
    {
        const string &sentence = sentences[k];
        int len = sentence.length();
        for (int i = 0; i <= len - SHINGLE_SIZE; i++)
        {
            string shingle = sentence.substr(i, SHINGLE_SIZE);
            if (shingleExists(vocabulary, vocabSize, shingle) == -1)
            {
                vocabulary[vocabSize] = shingle;
                vocabSize++;
            }
        }
    }
    return vocabSize;
}

void createOneHotVector(int vocabSize, int *oneHotVector, string &sentence, string *vocabulary)
{
    for (int i = 0; i < vocabSize; i++)
        oneHotVector[i] = 0;

    for (int i = 0; i <= sentence.length() - SHINGLE_SIZE; i++)
    {
        string shingle = sentence.substr(i, SHINGLE_SIZE);

        int index = shingleExists(vocabulary, vocabSize, shingle);
        if (index != -1)
            oneHotVector[index] = 1;
    }
}

void generatePermutations(int size, int numPermutations, int permutations[][100])
{
    for (int i = 0; i < numPermutations; i++)
    {
        int perm[100];
        for (int j = 0; j < size; j++)
            perm[j] = j;

        for (int j = size - 1; j > 0; j--)
        {
            int r = rand() % (j + 1);
            swap(perm[j], perm[r]);
        }

        for (int j = 0; j < size; j++)
            permutations[i][j] = perm[j];
    }
}

void minHashing(int *oneHotVector, int *denseVector, int vocabSize, int permutations[][100])
{
    for (int i = 0; i < PERMUTATIONS; i++)
    {
        denseVector[i] = vocabSize + 1;
        for (int j = 0; j < vocabSize; j++)
        {
            if (oneHotVector[j] == 1)
            {
                int permutedIndex = permutations[i][j];
                denseVector[i] = min(denseVector[i], permutedIndex);
            }
        }
    }
}

double cosineSimilarity(int *DV1, int *DV2)
{
    int dotProduct = 0;
    int value1 = 0, value2 = 0;
    for (int i = 0; i < PERMUTATIONS; i++)
    {
        dotProduct = dotProduct + DV1[i] * DV2[i];
        value1 = value1 + DV1[i] * DV1[i];
        value2 = value2 + DV2[i] * DV2[i];
    }
    return dotProduct / (sqrt(value1) * sqrt(value2));
}

int main()
{
#ifndef ONLINE_JUDGE
    freopen("input.txt", "r", stdin);
    freopen("output.txt", "w", stdout);
#endif

    string sentences[SENTENCES];
    for (int i = 0; i < SENTENCES; i++)
        getline(cin, sentences[i]);

    string vocabulary[100];
    int vocabSize = createVocabulary(sentences, vocabulary);

    cout << "Edit Distances: " << endl;
    for (int i = 0; i < SENTENCES; i++)
        for (int j = i + 1; j < SENTENCES; j++)
            cout << "Edit distance between " << i + 1 << " and " << j + 1 << " is " << editDistance(sentences[i], sentences[j]) << endl;

    cout << endl;

    int permutations[PERMUTATIONS][100];
    generatePermutations(vocabSize, PERMUTATIONS, permutations);

    cout << "Cosine Similarities: " << endl;
    int denseVectors[SENTENCES][PERMUTATIONS];
    for (int i = 0; i < SENTENCES; i++)
    {
        int oneHotVector[100];

        createOneHotVector(vocabSize, oneHotVector, sentences[i], vocabulary);

        minHashing(oneHotVector, denseVectors[i], vocabSize, permutations);
    }

    for (int i = 0; i < SENTENCES; i++)
        for (int j = i + 1; j < SENTENCES; j++)
            cout << "Cosine similarity between " << i + 1 << " and " << j + 1 << " is " << cosineSimilarity(denseVectors[i], denseVectors[j]) << endl;

    return 0;
}