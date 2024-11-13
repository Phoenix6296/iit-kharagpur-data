#include <iostream>
#include <climits>
using namespace std;

class Node
{
public:
    int data;
    Node *left, *right;
    Node(int value)
    {
        data = value;
        left = right = nullptr;
    }
};

class NodeValue
{
public:
    int maxNode, minNode, maxSize;
    bool isBST;

    NodeValue(int minNode, int maxNode, int maxSize, bool isBST)
    {
        this->maxNode = maxNode;
        this->minNode = minNode;
        this->maxSize = maxSize;
        this->isBST = isBST;
    }
};

NodeValue largestBSTSubtreeHelper(Node *root)
{
    if (!root)
        return NodeValue(INT_MAX, INT_MIN, 0, true);
    NodeValue left = largestBSTSubtreeHelper(root->left);
    NodeValue right = largestBSTSubtreeHelper(root->right);
    if (left.isBST && right.isBST && left.maxNode < root->data && root->data < right.minNode)
        return NodeValue(
            min(root->data, left.minNode),
            max(root->data, right.maxNode),
            left.maxSize + right.maxSize + 1,
            true);
    return NodeValue(INT_MIN, INT_MAX, max(left.maxSize, right.maxSize), false);
}

int largestBSTSubtree(Node *root)
{
    return largestBSTSubtreeHelper(root).maxSize;
}

Node *buildTreeFromInPre(int *preOrder, int *inOrder, int start, int end, int &preOrderRootIndex, int n)
{
    if (start > end || preOrderRootIndex >= n)
        return nullptr;
    Node *root = new Node(preOrder[preOrderRootIndex++]);
    int rootIndex = start;
    while (rootIndex <= end && inOrder[rootIndex] != root->data)
        rootIndex++;
    root->left = buildTreeFromInPre(preOrder, inOrder, start, rootIndex - 1, preOrderRootIndex, n);
    root->right = buildTreeFromInPre(preOrder, inOrder, rootIndex + 1, end, preOrderRootIndex, n);

    return root;
}

void display(int *arr, int n)
{
    for (int i = 0; i < n; i++)
        cout << arr[i] << " ";
    cout << endl;
}

int main()
{
#ifndef ONLINE_JUDGE
    freopen("input.txt", "r", stdin);
    freopen("output.txt", "w", stdout);
#endif

    int n;
    cin >> n;
    int inOrder[n];
    for (int i = 0; i < n; i++)
        cin >> inOrder[i];
    int preOrder[n];
    for (int i = 0; i < n; i++)
        cin >> preOrder[i];

    int index = 0;
    Node *root = buildTreeFromInPre(preOrder, inOrder, 0, n - 1, index, n);
    cout << "The size of the largest BST is " << largestBSTSubtree(root) << endl;

    return 0;
}
