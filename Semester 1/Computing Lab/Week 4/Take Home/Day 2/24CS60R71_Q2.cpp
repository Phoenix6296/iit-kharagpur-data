#include <iostream>
using namespace std;

class AVL
{
public:
    class node
    {
    public:
        int data, height;
        node *left, *right;
        node(int value)
        {
            height = 1;
            data = value;
            left = NULL;
            right = NULL;
        }
    };

    class Queue
    {
        node **arr;
        int front, rear, capacity;

    public:
        Queue(int size)
        {
            front = rear = 0;
            capacity = size;
            arr = new node *[capacity];
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
        void enqueue(node *root)
        {
            if (!isFull())
                arr[rear++] = root;
        }
        node *dequeue()
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

    node *root = NULL;
    int n;
    void insert(int x)
    {
        root = insertHelper(root, x);
    }
    void remove(int x)
    {
        root = removeHelper(root, x);
    }
    node *search(int x)
    {
        return searchHelper(root, x);
    }
    void preOrder()
    {
        cout << "Preorder: ";
        preOrder(root);
        cout << endl;
    }
    void inOrder()
    {
        cout << "Inorder: ";
        inOrder(root);
        cout << endl;
    }
    void postOrder()
    {
        cout << "Postorder: ";
        postOrder(root);
        cout << endl;
    }
    void levelOrder()
    {
        cout << "Level order: ";
        levelOrder(root);
        cout << endl;
    }
    void zigZagOrder()
    {
        cout << "Zig zag order: ";
        zigZagOrder(root);
        cout << endl;
    }

    void height()
    {
        int h = heightOfTree(root);
        if (h != 0)
            h--;
        cout << "The height of the tree is " << h << endl;
    }

    void burn()
    {
        int targetNode;
        cin >> targetNode;

        int time = 0;
        burnTree(root, targetNode, time);

        cout << "Total time = " << time << endl;
    }

private:
    int height(node *head)
    {
        if (head == NULL)
            return 0;
        return head->height;
    }

    void levelOrder(node *root)
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
                node *temp = helper.dequeue();
                cout << temp->data << " ";
                if (temp->left)
                    helper.enqueue(temp->left);
                if (temp->right)
                    helper.enqueue(temp->right);
            }
        }
    }

    void preOrder(node *root)
    {
        if (!root)
            return;
        cout << root->data << " ";
        preOrder(root->left);
        preOrder(root->right);
    }

    void inOrder(node *root)
    {
        if (!root)
            return;
        inOrder(root->left);
        cout << root->data << " ";
        inOrder(root->right);
    }

    void postOrder(node *root)
    {
        if (!root)
            return;
        postOrder(root->left);
        postOrder(root->right);
        cout << root->data << " ";
    }

    void zigZagOrder(node *root)
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
                node *temp = helper.dequeue();
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

    int heightOfTree(node *root)
    {
        if (!root)
            return 0;
        int left = heightOfTree(root->left);
        int right = heightOfTree(root->right);
        return 1 + max(left, right);
    }

    node *insertHelper(node *head, int key)
    {
        if (head == NULL)
        {
            n += 1;
            node *temp = new node(key);
            return temp;
        }
        if (key < head->data)
            head->left = insertHelper(head->left, key);
        else if (key > head->data)
            head->right = insertHelper(head->right, key);

        return head;
    }
    node *removeHelper(node *head, int x)
    {
        if (head == NULL)
            return NULL;
        if (x < head->data)
            head->left = removeHelper(head->left, x);
        else if (x > head->data)
            head->right = removeHelper(head->right, x);
        else
        {
            node *r = head->right;
            if (head->right == NULL)
            {
                node *l = head->left;
                delete (head);
                head = l;
            }
            else if (head->left == NULL)
            {
                delete (head);
                head = r;
            }
            else
            {
                while (r->left != NULL)
                    r = r->left;
                head->data = r->data;
                head->right = removeHelper(head->right, r->data);
            }
        }
        return head;
    }
    
    node *searchHelper(node *head, int x)
    {
        if (head == NULL)
            return NULL;
        int k = head->data;
        if (k == x)
            return head;
        if (k > x)
            return searchHelper(head->left, x);
        if (k < x)
            return searchHelper(head->right, x);

        return nullptr;
    }

    int burnTree(node *root, int targetNode, int &totalTime)
    {
        if (root == NULL)
            return -1;

        if (root->data == targetNode)
        {
            int leftHeight = burnChildNodes(root->left, 1, totalTime);
            int rightHeight = burnChildNodes(root->right, 1, totalTime);
            totalTime = max(leftHeight, rightHeight);
            return 1;
        }

        int leftTime = burnTree(root->left, targetNode, totalTime);
        if (leftTime != -1)
        {
            int rightHeight = burnChildNodes(root->right, leftTime + 1, totalTime);
            totalTime = max(totalTime, leftTime + rightHeight);
            return leftTime + 1;
        }

        int rightTime = burnTree(root->right, targetNode, totalTime);
        if (rightTime != -1)
        {
            int leftHeight = burnChildNodes(root->left, rightTime + 1, totalTime);
            totalTime = max(totalTime, rightTime + leftHeight);
            return rightTime + 1;
        }

        return -1;
    }
    int burnChildNodes(node *root, int time, int &totalTime)
    {
        if (root == NULL)
            return 0;

        int leftHeight = burnChildNodes(root->left, time + 1, totalTime);
        int rightHeight = burnChildNodes(root->right, time + 1, totalTime);
        totalTime = max(totalTime, time);
        return 1 + max(leftHeight, rightHeight);
    }
};

int main()
{
#ifndef ONLINE_JUDGE
    freopen("input.txt", "r", stdin);
    freopen("output.txt", "w", stdout);
#endif

    AVL t;
    while (true)
    {
        int choice;
        cin >> choice;
        if (choice == 1)
        {
            int key;
            cin >> key;
            t.insert(key);
        }
        else if (choice == 2)
        {
            int key;
            cin >> key;
            if (t.search(key))
                cout << "Found" << endl;
            else
                cout << "Not Found" << endl;
        }
        else if (choice == 3)
        {
            int key;
            cin >> key;
            t.remove(key);
        }
        else if (choice == 4)
            t.height();
        else if (choice == 5)
            t.preOrder();
        else if (choice == 6)
            t.postOrder();
        else if (choice == 7)
            t.inOrder();
        else if (choice == 8)
            t.levelOrder();
        else if (choice == 9)
            t.zigZagOrder();
        else if (choice == 10)
            break;
        else
            cout << "Enter the correct option again!!" << endl;
    }

    t.burn();
    return 0;
}