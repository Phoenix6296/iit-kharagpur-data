#include <iostream>
#define MAX 100
using namespace std;

int pathP[MAX][MAX];
string grid[MAX];

class queue
{
private:
    int front, rear, size, capacity;
    int *arr;

public:
    queue(int size)
    {
        capacity = size;
        front = 0, size = 0, rear = size - 1;
        arr = new int[capacity];
    }
    bool isEmpty() { return size == 0; }
    void enqueue(int data)
    {
        if (size == capacity)
            return;
        rear = (rear + 1) % capacity;
        arr[rear] = data;
        size++;
    }
    int dequeue()
    {
        if (!isEmpty())
        {
            int element = arr[front];
            front = (front + 1) % capacity;
            size--;
            return element;
        }
        return -1;
    }
};

class Solution
{
    int pathS[MAX][MAX], dist[MAX][MAX];

public:
    Solution(int m, int n)
    {
        for (int i = 0; i < m; i++)
            for (int j = 0; j < n; j++)
                pathP[i][j] = -1, dist[i][j] = -1;
    }
    bool check(int i, int j, int m, int n)
    {
        if (i == 0 or i == m - 1 or j == 0 or j == n - 1)
            return true;
        return false;
    }

    void bfs(int m, int n, int X, int Y)
    {
        queue q1(m * n), q2(m * n);
        q1.enqueue(X), q2.enqueue(Y);

        dist[X][Y] = 0;

        while (!q1.isEmpty() and !q2.isEmpty())
        {
            int x = q1.dequeue(), y = q2.dequeue();

            // Moving up
            int xNode = x - 1, yNode = y;
            if (xNode >= 0 and xNode < m and yNode >= 0 and yNode < n and grid[xNode][yNode] != '*' and dist[xNode][yNode] == -1)
            {
                dist[xNode][yNode] = dist[x][y] + 1;
                q1.enqueue(xNode), q2.enqueue(yNode);
            }

            // Moving down
            xNode = x + 1, yNode = y;
            if (xNode >= 0 and xNode < m and yNode >= 0 and yNode < n and grid[xNode][yNode] != '*' and dist[xNode][yNode] == -1)
            {
                dist[xNode][yNode] = dist[x][y] + 1;
                q1.enqueue(xNode), q2.enqueue(yNode);
            }

            // Moving left
            xNode = x, yNode = y - 1;
            if (xNode >= 0 and xNode < m and yNode >= 0 and yNode < n and grid[xNode][yNode] != '*' and dist[xNode][yNode] == -1)
            {
                dist[xNode][yNode] = dist[x][y] + 1;
                q1.enqueue(xNode), q2.enqueue(yNode);
            }

            xNode = x, yNode = y + 1;
            if (xNode >= 0 and xNode < m and yNode >= 0 and yNode < n and grid[xNode][yNode] != '*' and dist[xNode][yNode] == -1)
            {
                dist[xNode][yNode] = dist[x][y] + 1;
            }
        }
    }

    bool canEscape(int m, int n)
    {
        for (int i = 0; i < m; i++)
            for (int j = 0; j < n; j++)
                if ((grid[i][j] == '.' or grid[i][j] == 'S') and
                    pathS[i][j] != -1 and
                    (pathP[i][j] == -1 or pathS[i][j] < pathP[i][j]) and
                    check(i, j, m, n))
                    return true;
        return false;
    }
};

int main()
{

#ifndef ONLINE_JUDGE
    freopen("input3.txt", "r", stdin);
    freopen("output3.txt", "w", stdout);
#endif
    int n, m;
    cin >> m >> n;

    int X, Y;

    for (int i = 0; i < m; i++)
    {
        string s;
        cin >> s;
        grid[i] = s;
    }

    for (int i = 0; i < m; i++)
        for (int j = 0; j < n; j++)
            if (grid[i][j] == 'S')
                X = i, Y = j;

    Solution s(m, n);
    s.bfs(m, n, X, Y);

    for (int i = 0; i < m; i++)
        for (int j = 0; j < n; j++)
            if (grid[i][j] == 'P')
                s.bfs(m, n, i, j);

    s.canEscape(m, n) ? cout << "YES" : cout << "NO";

    return 0;
}
