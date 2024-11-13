#include <iostream>
using namespace std;

class Node
{
public:
    int data;
    Node *left, *right;
    Node(int value)
    {
        data = value;
        left = right = NULL;
    }
};

class QueueNode
{
public:
    Node *treeNode;
    int horizontalDistance;
    QueueNode *next;

    QueueNode(Node *n, int hd = 0)
    {
        treeNode = n;
        horizontalDistance = hd;
        next = NULL;
    }
};

class Queue
{
public:
    QueueNode *front, *rear;

    Queue()
    {
        front = rear = NULL;
    }

    void enqueue(Node *n, int hd = 0)
    {
        QueueNode *temp = new QueueNode(n, hd);
        if (rear == NULL)
        {
            front = rear = temp;
            return;
        }
        rear->next = temp;
        rear = temp;
    }

    QueueNode *dequeue()
    {
        if (front == NULL)
            return NULL;

        QueueNode *temp = front;
        front = front->next;

        if (front == NULL)
            rear = NULL;

        return temp;
    }

    bool isEmpty()
    {
        return front == NULL;
    }

    int size()
    {
        QueueNode *temp = front;
        int count = 0;
        while (temp != NULL)
        {
            count++;
            temp = temp->next;
        }
        return count;
    }
};

class TreeTraversals
{
    void leftBoundary(Node *root)
    {
        if (!root)
            return;

        if (root->left)
        {
            cout << root->data << " ";
            leftBoundary(root->left);
        }
        else if (root->right)
        {
            cout << root->data << " ";
            leftBoundary(root->right);
        }
    }

    void rightBoundary(Node *root)
    {
        if (!root)
            return;

        if (root->right)
        {
            rightBoundary(root->right);
            cout << root->data << " ";
        }
        else if (root->left)
        {
            rightBoundary(root->left);
            cout << root->data << " ";
        }
    }

    void printLeaves(Node *root)
    {
        if (!root)
            return;

        printLeaves(root->left);

        if (!(root->left) && !(root->right))
            cout << root->data << " ";

        printLeaves(root->right);
    }

    int search(int arr[], int start, int end, int value)
    {
        for (int i = start; i <= end; i++)
            if (arr[i] == value)
                return i;
        return -1;
    }

    Node *buildTree(int inorder[], int preorder[], int inorderStart, int inorderEnd, int &preorderIndex)
    {
        if (inorderStart > inorderEnd)
            return NULL;

        Node *node = new Node(preorder[preorderIndex++]);

        if (inorderStart == inorderEnd)
            return node;

        int inorderIndex = search(inorder, inorderStart, inorderEnd, node->data);

        node->left = buildTree(inorder, preorder, inorderStart, inorderIndex - 1, preorderIndex);
        node->right = buildTree(inorder, preorder, inorderIndex + 1, inorderEnd, preorderIndex);

        return node;
    }

public:
    Node *buildTree(int inorder[], int preorder[], int n)
    {
        int preorderIndex = 0;
        return buildTree(inorder, preorder, 0, n - 1, preorderIndex);
    }
    void verticalTopAndBottomView(Node *root, string direction)
    {
        if (!root)
            return;

        int columns[201][100];
        int counts[201] = {0};

        int minColumn = 100, maxColumn = 100;

        Queue q;
        q.enqueue(root, 100);

        while (!q.isEmpty())
        {
            QueueNode *temp = q.dequeue();
            Node *current = temp->treeNode;
            int hd = temp->horizontalDistance;

            columns[hd][counts[hd]++] = current->data;

            if (current->left)
                q.enqueue(current->left, hd - 1);
            if (current->right)
                q.enqueue(current->right, hd + 1);

            hd < minColumn ? minColumn = hd : maxColumn = hd;
        }

        for (int i = minColumn; i <= maxColumn; ++i)
        {
            for (int j = 0; j < counts[i]; ++j)
            {
                if (direction == "vertical")
                    cout << columns[i][j] << " ";
                else if (direction == "top" and j == 0)
                    cout << columns[i][j] << " ";
                else if (direction == "bottom" and j == counts[i] - 1)
                    cout << columns[i][counts[i] - 1] << " ";
            }
            if (direction == "vertical")
                cout << endl;
        }
        cout << endl;
    }

    void leftAndRightView(Node *root, string direction)
    {
        if (!root)
            return;
        Queue helper;
        helper.enqueue(root);

        while (!helper.isEmpty())
        {
            int size = helper.size();
            for (int i = 0; i < size; i++)
            {
                QueueNode *node = helper.dequeue();
                if ((direction == "left" && i == 0) || (direction == "right" && i == size - 1))
                    cout << node->treeNode->data << " ";

                if (node->treeNode->left)
                    helper.enqueue(node->treeNode->left);
                if (node->treeNode->right)
                    helper.enqueue(node->treeNode->right);
            }
        }
        cout << endl;
    }

    void boundaryTraversal(Node *root)
    {
        if (root == NULL)
            return;
        cout << root->data << " ";

        leftBoundary(root->left);

        printLeaves(root->left);
        printLeaves(root->right);

        rightBoundary(root->right);

        cout << endl;
    }
};

int main()
{
#ifndef ONLINE_JUDGE
    freopen("input.txt", "r", stdin);
    freopen("output.txt", "w", stdout);
#endif
    int n;
    cin >> n;

    int preorder[n], inorder[n];

    for (int i = 0; i < n; i++)
        cin >> inorder[i];
    for (int i = 0; i < n; i++)
        cin >> preorder[i];

    TreeTraversals t;

    Node *root = t.buildTree(inorder, preorder, n);

    cout << "Vertical Order: " << endl;
    t.verticalTopAndBottomView(root, "vertical");

    cout << "Right View: ";
    t.leftAndRightView(root, "right");

    cout << "Left View: ";
    t.leftAndRightView(root, "left");

    cout << "Top View: ";
    t.verticalTopAndBottomView(root, "top");

    cout << "Bottom View: ";
    t.verticalTopAndBottomView(root, "bottom");

    cout << "Boundary Traversal: ";
    t.boundaryTraversal(root);

    return 0;
}
