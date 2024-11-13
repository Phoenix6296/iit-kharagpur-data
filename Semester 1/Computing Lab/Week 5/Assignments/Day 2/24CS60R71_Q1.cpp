#include <iostream>
#include <fstream>
using namespace std;

typedef unsigned char u_char;

class TrieNode
{
public:
    char data;
    TrieNode *children[256];
    bool isTerminal;
    int rank;

    TrieNode(char value)
    {
        data = value;
        isTerminal = false;
        rank = 0;
        for (int i = 0; i < 256; i++)
            children[i] = nullptr;
    }
};

class Trie
{
    TrieNode *root;

    // Utility Functions
    bool isValidASCII(const string &word)
    {
        for (char c : word)
            if ((u_char)c > 127)
                return false;
        return true;
    }

    TrieNode *getNodeForPrefix(TrieNode *root, const string &prefix)
    {
        TrieNode *current = root;
        for (char c : prefix)
        {
            current = current->children[(u_char)c];
            if (!current)
                return nullptr;
        }
        return current;
    }

    void collectWords(TrieNode *node, string currentPrefix, string words[], int ranks[], int &count)
    {
        if (node->isTerminal)
        {
            words[count] = currentPrefix;
            ranks[count] = node->rank;
            count++;
        }

        for (int i = 0; i < 256; i++)
            if (node->children[i])
                collectWords(node->children[i], currentPrefix + (char)i, words, ranks, count);
    }

    void sortWords(string *words, int *ranks, int count)
    {
        for (int i = 0; i < count - 1; i++)
            for (int j = 0; j < count - i - 1; j++)
                if (ranks[j] < ranks[j + 1] or
                    (ranks[j] == ranks[j + 1] and words[j] > words[j + 1]))
                    swap(words[j], words[j + 1]),
                        swap(ranks[j], ranks[j + 1]);
    }

    void updateRanks(const string *words, int count)
    {
        for (int i = 0; i < count; i++)
        {
            TrieNode *node = getNodeForPrefix(root, words[i]);
            if (node and node->isTerminal)
                node->rank++;
        }
    }

    void findBestMatch(TrieNode *node, const string &target, string currentPrefix, int *dp, string &bestWord, int &bestRank)
    {
        int len = target.length();
        int newDp[len + 1];

        newDp[0] = dp[0] + 1;
        for (int i = 1; i <= len; i++)
        {
            int cost = (target[i - 1] == node->data) ? 0 : 1;
            newDp[i] = min(newDp[i - 1] + 1, min(dp[i] + 1, dp[i - 1] + cost));
        }

        if (node->isTerminal and newDp[len] <= 3)
            if (bestRank < node->rank or (bestRank == node->rank and currentPrefix < bestWord))
                bestWord = currentPrefix,
                bestRank = node->rank;

        int minDist = newDp[0];
        for (int i = 1; i <= len; i++)
            if (newDp[i] < minDist)
                minDist = newDp[i];

        if (minDist > 3)
            return;

        for (int i = 0; i < 256; i++)
            if (node->children[i])
                findBestMatch(node->children[i], target, currentPrefix + (char)i, newDp, bestWord, bestRank);
    }

    // Implementation Functions
    void addUtil(TrieNode *root, const string &word)
    {
        if (word.length() == 0)
        {
            root->isTerminal = true;
            root->rank++;
            return;
        }
        u_char index = word[0];
        TrieNode *child;

        if (root->children[index])
            child = root->children[index];
        else
        {
            child = new TrieNode(index);
            root->children[index] = child;
        }
        addUtil(child, word.substr(1));
    }

    void deleteUtil(TrieNode *root, const string &word)
    {
        if (word.length() == 0)
        {
            if (root->isTerminal)
                root->isTerminal = false;
            else
                cout << "Word not found!!" << endl;
            return;
        }
        u_char index = word[0];
        TrieNode *child = root->children[index];

        if (!child)
            return;

        deleteUtil(child, word.substr(1));
    }

    bool spellCheckUtil(TrieNode *root, const string &word)
    {
        if (word.length() == 0)
        {
            if (root->isTerminal)
            {
                root->rank++;
                return true;
            }
            return false;
        }

        u_char index = word[0];
        TrieNode *child = root->children[index];
        if (!child)
            return false;

        return spellCheckUtil(child, word.substr(1));
    }

    void autoCompleteUtil(TrieNode *root, const string &prefix)
    {
        string words[10000];
        int ranks[10000];
        int count = 0;

        TrieNode *node = getNodeForPrefix(root, prefix);

        if (node)
            collectWords(node, prefix, words, ranks, count);

        sortWords(words, ranks, count);

        for (int i = 0; i < count and i < 5; i++)
            cout << words[i] << endl;

        updateRanks(words, min(5, count));
    }

    void autoCorrectUtil(TrieNode *root, const string &target)
    {
        int len = target.length();
        int dp[len + 1];
        for (int i = 0; i <= len; i++)
            dp[i] = i;

        string bestWord;
        int bestRank = -1;

        for (int i = 0; i < 256; i++)
            if (root->children[i])
                findBestMatch(root->children[i], target, string(1, (char)i), dp, bestWord, bestRank);

        if (!bestWord.empty())
        {
            cout << bestWord << " (Rank: " << bestRank << ")" << endl;
            updateRanks(&bestWord, 1);
        }
        else
            cout << "No word found within distance " << 3 << endl;
    }

    bool checkConcatenationUtil(TrieNode *root, const string &word)
    {
        int n = word.length();
        for (int i = 1; i < n; i++)
        {
            string prefix = word.substr(0, i);
            string suffix = word.substr(i);

            if (spellCheckUtil(root, prefix) and spellCheckUtil(root, suffix))
                return 1;
        }
        return 0;
    }

public:
    Trie()
    {
        root = new TrieNode('\0');
    }

    void loadWordsFromFile(Trie *t, const string &filename)
    {
        ifstream file(filename);
        if (!file.is_open())
            return;
        string word;
        while (file >> word)
            t->Add(word);

        file.close();
    }

    void Add(const string &word)
    {
        if (isValidASCII(word))
            addUtil(root, word);
    }

    void Delete(const string &word)
    {
        if (isValidASCII(word))
            deleteUtil(root, word);
    }

    void SpellCheck(const string &word)
    {
        if (spellCheckUtil(root, word))
            cout << "1" << endl;
        else
        {
            Add(word);
            cout << "Not Found" << endl;
        }
    }

    void AutoComplete(const string &prefix)
    {
        autoCompleteUtil(root, prefix);
    }

    void AutoCorrect(const string &target)
    {
        autoCorrectUtil(root, target);
    }

    void CheckConcatenation(const string &word)
    {
        cout << checkConcatenationUtil(root, word) << endl;
    }
};
int main()
{
#ifndef ONLINE_JUDGE
    freopen("input.txt", "r", stdin);
    freopen("output.txt", "w", stdout);
#endif

    Trie *t = new Trie();
    t->loadWordsFromFile(t, "dict.bin");
    int choice;
    string word;

    int testcases;
    cin >> testcases;
    while (testcases--)
    {
        cin >> choice;

        switch (choice)
        {
        case 1:
            cin >> word;
            t->Add(word);
            break;

        case 2:
            cin >> word;
            t->Delete(word);
            break;

        case 3:
            cin >> word;
            t->SpellCheck(word);
            break;

        case 4:
            cin >> word;
            t->AutoComplete(word);
            break;

        case 5:
            cin >> word;
            t->AutoCorrect(word);
            break;

        case 6:
            cin >> word;
            t->CheckConcatenation(word);
            break;

        default:
            cout << "Invalid choice, please try again.\n";
            break;
        }
    }

    return 0;
}

// 12
// 1 krishna
// 1 krissha
// 1 hello

// 3 hello
// 3 krishn
// 3 krishn
// 4 kr
// 6 hellokrishna
// 6 hellokrisha
// 2 krishna
// 5 hilo
// 5 hsr