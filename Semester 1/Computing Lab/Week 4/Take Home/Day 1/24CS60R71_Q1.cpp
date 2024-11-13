#include <iostream>
using namespace std;

struct Node
{
    int data;
    Node *left, *right;
    Node(int data)
    {
        this->data = data;
        left = right = nullptr;
    }
};

int findHeight(Node *root)
{
    if (!root)
        return 0;
    int leftHeight = findHeight(root->left);
    int rightHeight = findHeight(root->right);
    return 1 + max(leftHeight, rightHeight);
}

void postOrder(Node *root)
{
    if (!root)
        return;
    postOrder(root->left);
    postOrder(root->right);
    cout << root->data << " ";
}

Node *buildTree(int *preOrder, int *inOrder, int start, int end, int &preIndex, int n)
{
    if (start > end or preIndex >= n)
        return nullptr;

    int rootValue = preOrder[preIndex++];
    Node *root = new Node(rootValue);

    if (start == end)
        return root;

    int inIndex;
    for (inIndex = start; inIndex <= end; ++inIndex)
        if (inOrder[inIndex] == rootValue)
            break;

    root->left = buildTree(preOrder, inOrder, start, inIndex - 1, preIndex, n);
    root->right = buildTree(preOrder, inOrder, inIndex + 1, end, preIndex, n);

    return root;
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

    int preIndex = 0;
    Node *root = buildTree(preOrder, inOrder, 0, n - 1, preIndex, n);

    cout << "Postorder: ";
    postOrder(root);
    cout << endl;

    int height = findHeight(root);
    cout << "Height: " << height << endl;

    return 0;
}
