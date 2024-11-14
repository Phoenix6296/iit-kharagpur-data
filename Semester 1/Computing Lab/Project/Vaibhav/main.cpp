#include "memfs.h"
#include <iostream>
#include <sstream>
#include <vector>
#include <string>
#include <chrono>
#include <iomanip>
#include <sys/resource.h>
#include <thread>
#include <functional>

// Parse the create command
void parseCreateCommand(std::istringstream &iss)
{
    std::string flag;
    int numFiles = 1;
    std::vector<std::string> filenames;

    if (iss >> flag && flag == "-n")
    {
        if (!(iss >> numFiles))
        {
            std::cerr << "Error: Invalid number after -n flag" << std::endl;
            return;
        }
    }
    else
    {
        filenames.push_back(flag);
    }

    std::string filename;
    while (filenames.size() < static_cast<std::size_t>(numFiles) && iss >> filename)
    {
        filenames.push_back(filename);
    }

    createFiles(numFiles, filenames);
}

// Parse the write command
void parseWriteCommand(std::istringstream &iss)
{
    std::string flag, filename, content;
    int numFiles = 1;
    std::vector<std::pair<std::string, std::string>> fileContentPairs;

    if (iss >> flag && flag == "-n")
    {
        iss >> numFiles;
    }
    else
    {
        iss.putback(flag[0]);
    }

    for (int i = 0; i < numFiles; ++i)
    {
        if (!(iss >> filename))
            break;
        std::getline(iss, content, '"');
        std::getline(iss, content, '"');
        fileContentPairs.emplace_back(filename, content);
    }

    writeToFile(fileContentPairs);
}

// Parse the delete command
void parseDeleteCommand(std::istringstream &iss)
{
    std::string flag;
    int numFiles = 1;
    std::vector<std::string> filenames;

    if (iss >> flag && flag == "-n")
    {
        if (!(iss >> numFiles))
        {
            std::cerr << "Error: Invalid number after -n flag" << std::endl;
            return;
        }
    }
    else
    {
        filenames.push_back(flag);
    }

    std::string filename;
    for (int i = filenames.size(); i < numFiles && iss >> filename; ++i)
    {
        filenames.push_back(filename);
    }

    for (const auto &file : filenames)
    {
        deleteFile(file);
    }
}

// Command loop to accept user inputs
void commandLoop()
{
    std::string line;
    while (std::cout << "memfs> ", std::getline(std::cin, line))
    {
        std::istringstream iss(line);
        std::string command;
        iss >> command;

        if (command == "create")
        {
            parseCreateCommand(iss);
        }
        else if (command == "write")
        {
            parseWriteCommand(iss);
        }
        else if (command == "delete")
        {
            parseDeleteCommand(iss);
        }
        else if (command == "read")
        {
            std::string filename;
            iss >> filename;
            readFile(filename);
        }
        else if (command == "ls")
        {
            bool detailed = (iss >> command && command == "-l");
            listFiles(detailed);
        }
        else if (command == "exit")
        {
            std::cout << "Exiting memFS" << std::endl;
            break;
        }
        else
        {
            std::cerr << "Unknown command" << std::endl;
        }
    }
}

// Prepare filenames and file data for the benchmark
void prepareData(int numFiles, std::vector<std::string> &filenames, std::vector<std::pair<std::string, std::string>> &fileData)
{
    for (int i = 0; i < numFiles; ++i)
    {
        filenames.push_back("file" + std::to_string(i));
        fileData.push_back({"file" + std::to_string(i), "Sample content"});
    }
}

// Run the benchmark with the specified number of files and threads

void runBenchmark(MemFS &fs, int numFiles, int numThreads)
{
    std::vector<std::string> filenames;
    std::vector<std::pair<std::string, std::string>> fileData;

    prepareData(numFiles, filenames, fileData);

    auto start = std::chrono::high_resolution_clock::now();

    // Step 1: Create files
    {
        std::vector<std::thread> threads;
        for (int i = 0; i < numThreads; ++i) {
            int startIdx = i * (numFiles / numThreads);
            int endIdx = (i == numThreads - 1) ? numFiles : startIdx + (numFiles / numThreads);

            if (startIdx < endIdx) {
                threads.emplace_back(&MemFS::createFiles, &fs, endIdx - startIdx,
                                     std::vector<std::string>(filenames.begin() + startIdx, filenames.begin() + endIdx));
            }
        }
        for (auto &t : threads) t.join();
    }

    // Step 2: Write to files
    {
        std::vector<std::thread> threads;
        for (int i = 0; i < numThreads; ++i) {
            int startIdx = i * (numFiles / numThreads);
            int endIdx = (i == numThreads - 1) ? numFiles : startIdx + (numFiles / numThreads);

            if (startIdx < endIdx) {
                threads.emplace_back(&MemFS::writeToFile, &fs, endIdx - startIdx,
                                     std::vector<std::pair<std::string, std::string>>(fileData.begin() + startIdx, fileData.begin() + endIdx));
            }
        }
        for (auto &t : threads) t.join();
    }

    // Step 3: Delete files
    {
        std::vector<std::thread> threads;
        for (int i = 0; i < numThreads; ++i) {
            int startIdx = i * (numFiles / numThreads);
            int endIdx = (i == numThreads - 1) ? numFiles : startIdx + (numFiles / numThreads);

            if (startIdx < endIdx) {
                threads.emplace_back(&MemFS::deleteFiles, &fs, endIdx - startIdx,
                                     std::vector<std::string>(filenames.begin() + startIdx, filenames.begin() + endIdx));
            }
        }
        for (auto &t : threads) t.join();
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    double avgLatency = duration / static_cast<double>(numFiles);

    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
    std::cout << "Number of Threads: " << numThreads << std::endl;
    std::cout << "Average Latency: " << avgLatency << " microseconds" << std::endl;
    std::cout << "CPU Usage: " << usage.ru_utime.tv_sec + usage.ru_utime.tv_usec / 1e6 << " seconds" << std::endl;
    std::cout << "Memory Usage: " << usage.ru_maxrss << " KB" << std::endl;
}

// Main function to perform benchmarking or command loop
int main()
{
    MemFS fs;
    std::cout << "Type 'benchmark' to run performance tests or 'commands' for interactive commands." << std::endl;
    std::string mode;
    std::cin >> mode;
    std::cin.ignore();

    if (mode == "benchmark")
    {
        int fileCounts[] = {100, 1000, 10000}; // Array for file counts
        std::cout << "Benchmarking MemFS:" << std::endl;
        for (int threads : {1, 2, 4, 8, 16})
        {
            for (int numFiles : fileCounts)
            {
                std::cout << "Benchmark with " << numFiles << " files, " << threads << " threads" << std::endl;
                runBenchmark(fs, numFiles, threads);
                std::cout << std::endl;
            }
        }
    }
    else if (mode == "commands")
    {
        commandLoop();
    }
    else
    {
        std::cerr << "Unknown mode selected." << std::endl;
    }

    return 0;
}
