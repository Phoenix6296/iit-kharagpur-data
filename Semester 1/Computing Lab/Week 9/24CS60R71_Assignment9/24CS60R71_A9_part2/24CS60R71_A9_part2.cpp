#include <iostream>
#include <thread>
#include <chrono>
#include <cstdlib>
#include <stdexcept>
#include <fstream>
#include <cmath>
#include <functional>
#include <vector>
#include <algorithm>

using namespace std;

class MathOperations
{
public:
    string addition(int x, int y) const
    {
        this_thread::sleep_for(chrono::seconds(3 + rand() % 5));
        return "Addition: " + to_string(x) + " + " + to_string(y) + " = " + to_string(x + y);
    }

    string subtraction(int x, int y) const
    {
        this_thread::sleep_for(chrono::seconds(3 + rand() % 5));
        return "Subtraction: " + to_string(x) + " - " + to_string(y) + " = " + to_string(x - y);
    }

    string multiplication(int x, int y) const
    {
        this_thread::sleep_for(chrono::seconds(3 + rand() % 5));
        return "Multiplication: " + to_string(x) + " * " + to_string(y) + " = " + to_string(x * y);
    }

    string division(int x, int y) const
    {
        if (y == 0)
            throw runtime_error("Division by zero");
        this_thread::sleep_for(chrono::seconds(3 + rand() % 5));
        return "Division: " + to_string(x) + " / " + to_string(y) + " = " + to_string(x / y);
    }

    string square_root(int x) const
    {
        if (x < 0)
            throw runtime_error("Square root of negative number");
        this_thread::sleep_for(chrono::seconds(3 + rand() % 5));
        return "Square root: √" + to_string(x) + " = " + to_string(sqrt(x));
    }
};

string exec_function(function<string(int, int)> fn, int x, int y)
{
    try
    {
        return fn(x, y);
    }
    catch (const exception &e)
    {
        return "Exception caught in thread: " + string(e.what());
    }
}

int main()
{
    srand(static_cast<unsigned int>(time(0)));
    MathOperations math_ops;

    double run_times[5];
    ofstream report("24CS60R71_part2_report.txt");

    report << "1.  Structure:  Sequential execution of mathematical operations using threads.\n\n";
    report << "2.  Input Format: Randomly generated numbers and mathematical operations (addition, subtraction, multiplication, division).\n\n";
    report << "3.  Output Format: Displayed results of the operations on the console, with exceptions handled by outputting messages.\n\n";
    report << "4.\n";

    for (int run = 0; run < 5; ++run)
    {
        function<string(int, int)> ops[500];
        int op_data[500][2];

        int i = 0;
        while (i < 500)
        {
            int x = rand() % 100;
            int y = rand() % 100;

            if (rand() % 10 == 0)
            {
                if (rand() % 2 == 0)
                {
                    ops[i] = bind(&MathOperations::division, math_ops, placeholders::_1, placeholders::_2);
                    y = 0;
                }
                else
                {
                    ops[i] = [math_ops](int x, int)
                    { return math_ops.square_root(x); };
                    x = -x;
                    y = 0;
                }
            }
            else
            {
                int op_choice = rand() % 4;

                if (op_choice == 0)
                {
                    ops[i] = bind(&MathOperations::addition, math_ops, placeholders::_1, placeholders::_2);
                }
                else if (op_choice == 1)
                {
                    ops[i] = bind(&MathOperations::subtraction, math_ops, placeholders::_1, placeholders::_2);
                }
                else if (op_choice == 2)
                {
                    ops[i] = bind(&MathOperations::multiplication, math_ops, placeholders::_1, placeholders::_2);
                }
                else // op_choice == 3
                {
                    ops[i] = bind(&MathOperations::division, math_ops, placeholders::_1, placeholders::_2);
                }
            }

            op_data[i][0] = x;
            op_data[i][1] = y;

            i++; // Increment index for while loop
        }

        auto start = chrono::high_resolution_clock::now();

        vector<thread> threads;
        i = 0;
        while (i < 500)
        {
            threads.emplace_back([=]()
                                 {
                             string result = exec_function(ops[i], op_data[i][0], op_data[i][1]);
                             cout << result << endl; });

            i++;
        }

        for (auto &th : threads)
        {
            th.join();
        }

        auto end = chrono::high_resolution_clock::now();
        double run_time = chrono::duration<double>(end - start).count();

        run_times[run] = run_time;
        report << "Time taken for run " << run + 1 << ": " << run_time << " seconds.\n";
    }

    double sum_times = 0.0;
    for (int i = 0; i < 5; i++)
        sum_times += run_times[i];
    double avg_time = sum_times / 5.0;

    sort(run_times, run_times + 5);

    // Calculate median
    double median = (run_times[2] + run_times[3]) / 2.0;

    // Calculate standard deviation
    double variance = 0.0;
    for (int i = 0; i < 5; ++i)
        variance += pow(run_times[i] - avg_time, 2);
    variance /= 5.0;
    double std_dev = sqrt(variance);

    // 95th percentile calculation
    double percentile_95th = run_times[4]; // Since it's a small array, 95th percentile is just the max value in the sorted array

    // Max time
    double max_time = run_times[4];

    report << "\nTotal run statistics for 5 runs:\n";
    report << "Average time: " << avg_time << " seconds.\n";
    report << "Standard deviation: " << std_dev << " seconds.\n";
    report << "Median time: " << median << " seconds.\n";
    report << "95th Percentile time: " << percentile_95th << " seconds.\n";
    report << "Max time: " << max_time << " seconds.\n";
    report.close();

    return 0;
}
