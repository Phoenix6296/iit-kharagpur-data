#include <iostream>
#include <limits.h>
using namespace std;

int minPathSum(int **maze, int currRow, int currCol, int rows, int cols, int **dp)
{
    if (dp[currRow][currCol] != -1)
        return dp[currRow][currCol];
    if (currRow >= rows || currCol >= cols)
        return INT_MAX;
    if (currRow == rows - 1 && currCol == cols - 1)
        return maze[currRow][currCol];

    int down = minPathSum(maze, currRow + 1, currCol, rows, cols, dp);
    int right = minPathSum(maze, currRow, currCol + 1, rows, cols, dp);

    return dp[currRow][currCol] = maze[currRow][currCol] + min(down, right);
}
int main()
{
    int n, m;
    cin >> n >> m;
    int **maze = new int *[n];
    for (int i = 0; i < n; i++)
        maze[i] = new int[m];

    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            cin >> maze[i][j];

    int **dp = new int *[n + 1];
    for (int i = 0; i < n + 1; i++)
        dp[i] = new int[m + 1];

    for (int i = 0; i < n + 1; i++)
        for (int j = 0; j < m + 1; j++)
            dp[i][j] = -1;

    cout << minPathSum(maze, 0, 0, n, m, dp) << endl;

    return 0;
}