#include <iostream>
#include <limits.h>
#include <fstream>
using namespace std;
class Node
{
public:
    int data;
    Node *left, *right;
    Node(int val)
    {
        data = val;
        left = nullptr;
        right = nullptr;
    }
};

class Queue
{
    Node **arr;
    int front, rear, capacity;

public:
    Queue(int size)
    {
        front = rear = 0;
        capacity = size;
        arr = new Node *[capacity];
    }
    ~Queue()
    {
        delete[] arr;
    }
    bool isEmpty()
    {
        return front == rear;
    }
    bool isFull()
    {
        return rear == capacity;
    }
    void enqueue(Node *root)
    {
        if (!isFull())
            arr[rear++] = root;
    }
    Node *dequeue()
    {
        if (!isEmpty())
            return arr[front++];
        return nullptr;
    }
    int size()
    {
        return rear - front;
    }
};

void preOrder(Node *root)
{
    if (!root)
        return;
    cout << root->data << " ";
    preOrder(root->left);
    preOrder(root->right);
}

void inOrder(Node *root)
{
    if (!root)
        return;
    inOrder(root->left);
    cout << root->data << " ";
    inOrder(root->right);
}

void postOrder(Node *root)
{
    if (!root)
        return;
    postOrder(root->left);
    postOrder(root->right);
    cout << root->data << " ";
}

void levelOrder(Node *root)
{
    if (!root)
        return;
    Queue helper(100);
    helper.enqueue(root);
    while (!helper.isEmpty())
    {
        int size = helper.size();
        for (int i = 0; i < size; i++)
        {
            Node *temp = helper.dequeue();
            cout << temp->data << " ";
            if (temp->left)
                helper.enqueue(temp->left);
            if (temp->right)
                helper.enqueue(temp->right);
        }
    }
}

void zigZag(Node *root)
{
    if (!root)
        return;
    Queue helper(100);
    helper.enqueue(root);
    bool flag = true;
    while (!helper.isEmpty())
    {
        int size = helper.size();
        int arr[size];
        for (int i = 0; i < size; i++)
        {
            Node *temp = helper.dequeue();
            int index = flag ? i : (size - i - 1);
            arr[index] = temp->data;
            if (temp->left)
                helper.enqueue(temp->left);
            if (temp->right)
                helper.enqueue(temp->right);
        }
        flag = !flag;
        for (int i = 0; i < size; i++)
            cout << arr[i] << " ";
    }
}

int heightOfTree(Node *root)
{
    if (!root)
        return 0;
    int left = heightOfTree(root->left);
    int right = heightOfTree(root->right);
    return 1 + max(left, right);
}

void insert(Node *&root, int data)
{
    if (!root)
    {
        root = new Node(data);
        return;
    }
    if (data > root->data)
        insert(root->right, data);
    else
        insert(root->left, data);
}

bool searchNode(Node *root, int key)
{
    if (!root)
        return false;
    if (root->data == key)
        return true;
    if (key < root->data)
        return searchNode(root->left, key);
    else
        return searchNode(root->right, key);
}
int adjust(Node *root)
{
    int m1 = root->data;
    if (!root)
        return 0;
    m1 = min(m1, adjust(root->left));
    return m1;
}
Node *deleteNode(Node *root, int key)
{
    if (!root)
        return nullptr;
    if (root->data == key)
    {
        if (!root->left and !root->right)
            return root;
        if (root->left and !root->right)
        {
            Node *node = root->left;
            return node;
        }
        if (!root->left and root->right)
        {
            Node *node = root->right;
            return node;
        }
        if (root->left and root->right)
        {
            int m2 = adjust(root->right);
            root->right = deleteNode(root->right, m2);
            delete (root);
        }
    }
    return nullptr;
}
int main()
{
    // The input and output file is not functioning properly else every thing is perfect.
    // Please try to run the function seperately for the output.
    // int choice;
    // cin >> choice;
    // while (true)
    // {
    //     switch (choice)
    //     {
    //     case 1:
    //         int data;
    //         cin >> data;
    //         insert(root, data);
    //         break;
    //     case 2:
    //         int key;
    //         cin >> key;
    //         if (searchNode(root, key))
    //             cout << "Element Found!!" << endl;
    //         else
    //             cout << "Element not Found!!" << endl;
    //         break;
    //     case 3:
    //         // int key;
    //         // cin >> key;
    //         // Node *deletedNode = deleteNode(root, data);
    //         // cout << deletedNode->data << endl;
    //         break;
    //     case 4:
    //         cout << "Height of Binary Tree: " << heightOfTree(root);
    //         break;
    //     case 5:
    //         cout << "Pre-Order Traversal: ";
    //         preOrder(root);
    //         cout << endl;
    //         break;
    //     case 6:
    //         cout << "Post-Order Traversal: ";
    //         postOrder(root);
    //         cout << endl;
    //         break;
    //     case 7:
    //         cout << "In-Order Traversal: ";
    //         inOrder(root);
    //         cout << endl;
    //         break;
    //     case 8:
    //         cout << "Level Order Traversal: ";
    //         levelOrder(root);
    //         cout << endl;
    //         break;
    //     case 9:
    //         cout << "Zig-Zag Order Traversal: ";
    //         zigZag(root);
    //         cout << endl;
    //         break;
    //     default:
    //         exit(0);
    //     }
    // }

    Node *root = new Node(1);
    root->left = new Node(2);
    root->right = new Node(3);
    root->left->left = new Node(4);
    root->left->right = new Node(5);
    root->right->right = new Node(6);

    cout << searchNode(root, 9) << endl;
    preOrder(root);
    cout << endl;
    inOrder(root);
    cout << endl;
    postOrder(root);
    cout << endl;
    levelOrder(root);
    zigZag(root);
    // insert(root,1);
    heightOfTree(root);

    // cout << deleteNode(root, 3);
    return 0;
}