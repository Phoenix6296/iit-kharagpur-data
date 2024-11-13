#include <iostream>

using namespace std;

const int MAX = 1000;
int dp[MAX][MAX];

int dfs(int row, int col, int m, int n, int mat[MAX][MAX])
{
    if (dp[row][col] != 0)
        return dp[row][col];

    int maxLength = 1;

    // Move Up
    if (row > 0 && mat[row - 1][col] > mat[row][col])
        maxLength = max(maxLength, 1 + dfs(row - 1, col, m, n, mat));

    // Move Left
    if (col > 0 && mat[row][col - 1] > mat[row][col])
        maxLength = max(maxLength, 1 + dfs(row, col - 1, m, n, mat));

    // Move Down
    if (row < m - 1 && mat[row + 1][col] > mat[row][col])
        maxLength = max(maxLength, 1 + dfs(row + 1, col, m, n, mat));

    // Move Right
    if (col < n - 1 && mat[row][col + 1] > mat[row][col])
        maxLength = max(maxLength, 1 + dfs(row, col + 1, m, n, mat));

    return dp[row][col] = maxLength;
}

int findMaxLength(int mat[MAX][MAX], int m, int n)
{
    for (int i = 0; i < m; i++)
        for (int j = 0; j < n; j++)
            dp[i][j] = 0;

    int maxPath = 1;
    for (int i = 0; i < m; i++)
        for (int j = 0; j < n; j++)
            maxPath = max(maxPath, dfs(i, j, m, n, mat));

    return maxPath;
}

int main()
{
#ifndef ONLINE_JUDGE
    freopen("input2.txt", "r", stdin);
    freopen("output2.txt", "w", stdout);
#endif
    int n, m;
    cin >> n >> m;

    int mat[MAX][MAX];

    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            cin >> mat[i][j];

    cout << findMaxLength(mat, n, m) << endl;

    return 0;
}
