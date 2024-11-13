#include <iostream>
#include <pthread.h>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <vector>
#include <algorithm>
#include <fstream>
#include <numeric>
#include <cmath>

using namespace std;

// Struct to hold input values and result for each operation
struct MathOperation
{
    int x;
    int y;
    double result;
};

// Mathematical operations
int add(int x, int y) { return x + y; }
int subtract(int x, int y) { return x - y; }
int multiply(int x, int y) { return x * y; }
double divide(double x, double y) { return x / y; }
double power(int x, int y) { return pow(x, y); }

// Wrapper functions for thread execution
class Wrapper
{
public:
    // Static wrapper functions to call non-static member functions
    static void *start_thread_add(void *arg)
    {
        MathOperation *op = (MathOperation *)arg;
        op->result = add(op->x, op->y);
        pthread_exit(nullptr);
    }

    static void *start_thread_subtract(void *arg)
    {
        MathOperation *op = (MathOperation *)arg;
        op->result = subtract(op->x, op->y);
        pthread_exit(nullptr);
    }

    static void *start_thread_multiply(void *arg)
    {
        MathOperation *op = (MathOperation *)arg;
        op->result = multiply(op->x, op->y);
        pthread_exit(nullptr);
    }

    static void *start_thread_divide(void *arg)
    {
        MathOperation *op = (MathOperation *)arg;
        op->result = divide(op->x, op->y);
        pthread_exit(nullptr);
    }

    static void *start_thread_power(void *arg)
    {
        MathOperation *op = (MathOperation *)arg;
        op->result = power(op->x, op->y);
        pthread_exit(nullptr);
    }
};

// Utility class remains unchanged
class Utility
{
public:
    double calculate_median(vector<double> &times)
    {
        sort(times.begin(), times.end());
        size_t n = times.size();
        if (n % 2 == 0)
            return (times[n / 2 - 1] + times[n / 2]) / 2.0;
        else
            return times[n / 2];
    }

    // Function to calculate 95th percentile
    double calculate_percentile(vector<double> &times, double percentile)
    {
        sort(times.begin(), times.end());
        size_t index = (size_t)ceil((percentile / 100.0) * times.size()) - 1;
        return times[index];
    }

    // Function to calculate standard deviation
    double calculate_standard_deviation(const vector<double> &times, double avg)
    {
        double variance = 0.0;
        for (double time : times)
            variance += pow(time - avg, 2);
        variance /= times.size();
        return sqrt(variance);
    }
};

int main()
{
    srand(time(0));

    int sampleSize = 500;
    int repetitions = 5;
    vector<double> avg_times, medians, std_devs, p95_times, max_times;

    Utility u;

    ofstream report("24CS60R71_part1_report.txt");

    report << "Structure:\n";
    report << "Struct MathOperation { int x, int y; double result; }\n\n";

    report << "Input format:\n";
    report << "Random integers x and y for each mathematical operation.\n\n";

    report << "Output format:\n";
    report << "Result of the operation stored in 'result' field of MathOperation struct.\n\n";

    // Perform the 500 operations 5 times
    for (int r = 0; r < repetitions; ++r)
    {
        vector<double> times;
        clock_t start, end;

        for (int i = 0; i < sampleSize; ++i)
        {
            MathOperation temp = {rand() % 100, rand() % 100 + 1}; // Random inputs

            // Pick a random operation to perform
            int choice = rand() % 5;
            start = clock();

            switch (choice)
            {
            case 0:
                temp.result = add(temp.x, temp.y);
                cout << "Operation: " << temp.x << " + " << temp.y << " = " << temp.result << endl;
                break;
            case 1:
                temp.result = subtract(temp.x, temp.y);
                cout << "Operation: " << temp.x << " - " << temp.y << " = " << temp.result << endl;
                break;
            case 2:
                temp.result = multiply(temp.x, temp.y);
                cout << "Operation: " << temp.x << " * " << temp.y << " = " << temp.result << endl;
                break;
            case 3:
                temp.result = divide(temp.x, temp.y);
                cout << "Operation: " << temp.x << " / " << temp.y << " = " << temp.result << endl;
                break;
            case 4:
                temp.result = power(temp.x, temp.y);
                cout << "Operation: " << temp.x << " ^ " << temp.y << " = " << temp.result << endl;
                break;
            }

            end = clock();
            times.push_back(double(end - start) / CLOCKS_PER_SEC);
        }

        // Calculate statistics for the current run
        double sum = accumulate(times.begin(), times.end(), 0.0);
        double avg = sum / sampleSize;
        double max_time = *max_element(times.begin(), times.end());
        double median = u.calculate_median(times);
        double percentile_95th = u.calculate_percentile(times, 95.0);
        double standard_deviation = u.calculate_standard_deviation(times, avg);

        // Store the results of this run
        avg_times.push_back(avg);
        medians.push_back(median);
        std_devs.push_back(standard_deviation);
        p95_times.push_back(percentile_95th);
        max_times.push_back(max_time);

        // Print run statistics for each repetition
        report << "Time taken for run " << r + 1 << ": " << avg << " seconds." << endl;
    }

    // Calculate overall statistics across all repetitions
    double final_avg = accumulate(avg_times.begin(), avg_times.end(), 0.0) / repetitions;
    double final_median = u.calculate_median(medians);
    double final_max = *max_element(max_times.begin(), max_times.end());
    double final_95th = u.calculate_percentile(p95_times, 95.0);
    double final_std_dev = u.calculate_standard_deviation(avg_times, final_avg);

    // Write the final statistics to a report file
    report << "\nFinal statistics across 5 repetitions of 500 operations:\n";
    report << "Average time: " << final_avg << " seconds\n";
    report << "Median time: " << final_median << " seconds\n";
    report << "Max time: " << final_max << " seconds\n";
    report << "95th percentile time: " << final_95th << " seconds\n";
    report << "Standard deviation: " << final_std_dev << " seconds\n";

    report.close();
    cout << "Report generated: 24CS60R71_part1_report.txt" << endl;

    return 0;
}
