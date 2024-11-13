#include <iostream>
#include <limits.h>
using namespace std;

int longestValidParentheses(string s)
{
    int left = 0, right = 0, ans = 0;

    for (int i = 0; i < s.size(); i++)
    {
        s[i] == '(' ? left++ : right++;
        if (left == right)
            ans = max(ans, left << 1);
        else if (right > left)
            left = 0, right = 0;
    }
    left = 0;
    right = 0;
    for (int i = s.size() - 1; i >= 0; --i)
    {
        s[i] == '(' ? left++ : right++;
        if (left == right)
            ans = max(ans, left << 1);
        else if (left > right)
            left = 0, right = 0;
    }
    return ans;
}

int main()
{
    string s;
    cin >> s;
    cout << longestValidParentheses(s) << endl;
    return 0;
}