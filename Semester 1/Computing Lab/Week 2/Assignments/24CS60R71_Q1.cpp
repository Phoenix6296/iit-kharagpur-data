#include <iostream>
#include <string>
#define ALPHABETS 26
using namespace std;

int main()
{
    int MOD = 1e9 + 7;
    int n;
    string s;
    cin >> n >> s;

    int a[ALPHABETS];
    for (int i = 0; i < ALPHABETS; i++)
        cin >> a[i];

    int dp[1001] = {0};
    dp[0] = 1;
    int minParts[1001] = {0};
    minParts[0] = 0;

    int maxLength = 0;

    for (int i = 0; i < n; i++)
    {
        int minLength = n;
        for (int j = i; j >= 0; j--)
        {
            int comparator = i - j + 1;

            if (a[s[j] - 97] < minLength)
                minLength = a[s[j] - 97];

            if (comparator > minLength)
                break;

            dp[i + 1] = (dp[i + 1] + dp[j]) % MOD;

            if (minParts[i + 1] == 0 or minParts[i + 1] > minParts[j] + 1)
                minParts[i + 1] = minParts[j] + 1;

            if (comparator > maxLength)
                maxLength = comparator;
        }
    }

    cout << dp[n] << endl
         << maxLength << endl
         << minParts[n] << endl;

    return 0;
}
