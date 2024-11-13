#include <iostream>
#include <limits.h>
using namespace std;

#define MAX 100
class Edge
{
public:
    int u, v, weight;
};

class graph
{
    void bubbleSort(Edge arr[], int size, bool ascending)
    {
        bool swapped;
        for (int i = 0; i < size - 1; i++)
        {
            swapped = false;
            for (int j = 0; j < size - i - 1; j++)
            {
                bool condition = ascending ? arr[j].weight > arr[j + 1].weight : arr[j].weight < arr[j + 1].weight;
                if (condition or
                    (arr[j].weight == arr[j + 1].weight and
                     (arr[j].u > arr[j + 1].u or
                      (arr[j].u == arr[j + 1].u and arr[j].v > arr[j + 1].v))))
                {
                    Edge temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                    swapped = true;
                }
            }
            if (!swapped)
                break;
        }
    }

public:
    int n;
    int adj[MAX][MAX];
    int weight[MAX][MAX];
    Edge edges[MAX * (MAX - 1) / 2];
    int edgeCount;

    graph(int size)
    {
        n = size;
        edgeCount = 0;
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                adj[i][j] = 0, weight[i][j] = 0;
    }

    void addEdge(int u, int v, int w)
    {
        if (u >= 0 and u < n and v >= 0 and v < n)
        {
            adj[u][v] = 1, adj[v][u] = 1;
            weight[u][v] = w, weight[v][u] = w;
            edges[edgeCount++] = {u, v, w};
        }
    }

    int find(int parent[], int i)
    {
        if (parent[i] == i)
            return i;
        return find(parent, parent[i]);
    }

    void Union(int parent[], int rank[], int x, int y)
    {
        int rootX = find(parent, x);
        int rootY = find(parent, y);

        if (rank[rootX] < rank[rootY])
            parent[rootX] = rootY;
        else if (rank[rootX] > rank[rootY])
            parent[rootY] = rootX;
        else
        {
            parent[rootY] = rootX;
            rank[rootX]++;
        }
    }

    void kruskals()
    {
        Edge result[MAX];
        int parent[MAX], rank[MAX];

        for (int i = 0; i < n; i++)
        {
            parent[i] = i;
            rank[i] = 0;
        }

        bubbleSort(edges, edgeCount, true); // Sort edges in ascending order

        int e = 0, i = 0;

        while (e < n - 1 and i < edgeCount)
        {
            Edge nextEdge = edges[i++];

            int x = find(parent, nextEdge.u);
            int y = find(parent, nextEdge.v);

            if (x != y)
            {
                result[e++] = nextEdge;
                Union(parent, rank, x, y);
            }
        }
        bubbleSort(result, e, false); // Sort result edges in descending order
        int sum = 0;
        for (int i = 0; i < e; i++)
        {
            sum += result[i].weight;
            cout << result[i].weight << " " << result[i].u << " " << result[i].v << " " << endl;
        }
        cout << "Weight of the MST: " << sum << endl;
    }

    void dijkstra(int start)
    {
        bool visited[MAX];
        for (int i = 0; i < MAX; i++)
            visited[i] = false;

        int parent[MAX], distance[MAX], count[MAX];

        for (int i = 0; i < n; i++)
        {
            parent[i] = -1;
            count[i] = 0;
            distance[i] = INT_MAX;
        }

        parent[start] = -1;
        distance[start] = 0;
        count[start] = 1;

        for (int l = 0; l < n - 1; l++)
        {

            int u = -1,
                minDist = INT_MAX;
            for (int i = 0; i < n; i++)
                if (!visited[i] and distance[i] < minDist)
                    minDist = distance[i], u = i;

            if (u == -1)
                return;

            visited[u] = true;
            for (int i = 0; i < n; i++)
            {
                int temp = distance[u] + weight[u][i];
                if (!visited[i] and adj[u][i] == 1)
                {
                    if (temp < distance[i])
                        count[i] = count[u], distance[i] = temp;
                    else if (temp == distance[i])
                        count[i] += count[u];
                }
            }
        }
        cout << "Shortest Path length: " << distance[n - 1] << endl;
        cout << "#Possible Shortest Paths: " << count[n - 1] << endl;
    }
};

int main()
{
#ifndef ONLINE_JUDGE
    freopen("input1.txt", "r", stdin);
    freopen("output1.txt", "w", stdout);
#endif
    int n, k;
    cin >> n >> k;

    graph g(n);
    for (int i = 0; i < k; i++)
    {
        int u, v, w;
        cin >> u >> v >> w;
        g.addEdge(u, v, w);
    }

    g.kruskals();
    g.dijkstra(0);

    return 0;
}
