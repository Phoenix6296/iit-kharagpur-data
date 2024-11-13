#include <iostream>
#include <string>

using namespace std;

int dp[1000][1000][1000];
void noOfZerosAndOnes(string &str, int &zeros, int &ones)
{
    zeros = 0, ones = 0;
    for (int i = 0; i < str.size(); i++)
        str[i] == '0' ? zeros++ : ones++;
}

int calculate(string *arr, int arraySize, int m, int n, int index)
{
    if (index >= arraySize)
        return 0;
    if (dp[index][m][n] != -1)
        return dp[index][m][n];

    int zeros, ones;
    noOfZerosAndOnes(arr[index], zeros, ones);

    int take = 0;
    if (m >= zeros and n >= ones)
        take = 1 + calculate(arr, arraySize, m - zeros, n - ones, index + 1);
    int notTake = calculate(arr, arraySize, m, n, index + 1);

    return dp[index][m][n] = max(take, notTake);
}

int main()
{
    int arraySize, m, n;
    cin >> arraySize;

    string arr[arraySize];
    for (int i = 0; i < arraySize; i++)
        cin >> arr[i];

    cin >> m >> n;
    for (int i = 0; i < arraySize; i++)
        for (int j = 0; j <= m; j++)
            for (int k = 0; k <= n; k++)
                dp[i][j][k] = -1;

    cout << calculate(arr, arraySize, m, n, 0) << endl;
    return 0;
}
