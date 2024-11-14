#include "memfs.h"
#include <iostream>
#include <iomanip>
#include <ctime>
#include <sstream>
#include <thread>

std::unordered_map<std::string, File> memFS;
std::mutex fsMutex;

void createFiles(int numFiles, const std::vector<std::string>& filenames) {
    std::lock_guard<std::mutex> lock(fsMutex);
    for (const auto& filename : filenames) {
        if (memFS.find(filename) == memFS.end()) {
            memFS[filename] = File();
            std::cout << "File \"" << filename << "\" created successfully." << std::endl;
        } else {
            std::cerr << "Error: File \"" << filename << "\" already exists." << std::endl;
        }
    }
}

void writeToFile(const std::vector<std::pair<std::string, std::string>>& fileContentPairs) {
    std::lock_guard<std::mutex> lock(fsMutex);
    for (const auto& [filename, content] : fileContentPairs) {
        if (memFS.find(filename) != memFS.end()) {
            memFS[filename].content = content;
            memFS[filename].lastModified = std::time(nullptr);
            std::cout << "Data written to file \"" << filename << "\" successfully." << std::endl;
        } else {
            std::cerr << "Error: File \"" << filename << "\" does not exist." << std::endl;
        }
    }
}

void deleteFile(const std::string& filename) {
    std::lock_guard<std::mutex> lock(fsMutex);
    if (memFS.erase(filename) > 0) {
        std::cout << "File \"" << filename << "\" deleted successfully." << std::endl;
    } else {
        std::cerr << "Error: File \"" << filename << "\" does not exist." << std::endl;
    }
}

void readFile(const std::string& filename) {
    std::lock_guard<std::mutex> lock(fsMutex);
    if (memFS.find(filename) != memFS.end()) {
        std::cout << "Reading file \"" << filename << "\":" << std::endl;
        std::cout << memFS[filename].content << std::endl;
    } else {
        std::cerr << "Error: File \"" << filename << "\" does not exist." << std::endl;
    }
}

void listFiles(bool detailed) {
    std::lock_guard<std::mutex> lock(fsMutex);
    for (const auto& [filename, file] : memFS) {
        if (detailed) {
            std::cout << filename << " | Created: " << std::put_time(std::localtime(&file.created), "%Y-%m-%d %H:%M:%S")
                      << " | Last Modified: " << std::put_time(std::localtime(&file.lastModified), "%Y-%m-%d %H:%M:%S")
                      << std::endl;
        } else {
            std::cout << filename << std::endl;
        }
    }
}

// Class-based MemFS helper methods
std::string MemFS::getCurrentDate() const {
    std::time_t now = std::time(0);
    std::tm* ltm = std::localtime(&now);
    std::stringstream date;
    date << std::setw(2) << std::setfill('0') << ltm->tm_mday << "/"
         << std::setw(2) << std::setfill('0') << (ltm->tm_mon + 1) << "/"
         << (1900 + ltm->tm_year);
    return date.str();
}

void MemFS::createFile(const std::string& filename) {
    std::lock_guard<std::mutex> lock(fsMutex);
    if (files.find(filename) != files.end()) {
        std::cerr << "Error: file with same name exists" << std::endl;
        return;
    }
    FileMetadata metadata = {"", 0, getCurrentDate(), getCurrentDate()};
    files[filename] = metadata;
    createdCount++;
}

void MemFS::writeFile(const std::string& filename, const std::string& data) {
    std::lock_guard<std::mutex> lock(fsMutex);
    if (files.find(filename) == files.end()) {
        std::cerr << "Error: " << filename << " does not exist" << std::endl;
        return;
    }
    files[filename].content = data;
    files[filename].size = data.size();
    files[filename].lastModified = getCurrentDate();
}

void MemFS::deleteFile(const std::string& filename) {
    std::lock_guard<std::mutex> lock(fsMutex);
    if (files.erase(filename) == 0)
        std::cerr << "Error: " << filename << " doesn’t exist" << std::endl;
}

void MemFS::createFiles(int numFiles, const std::vector<std::string>& filenames) {
    for (const auto& filename : filenames)
        createFile(filename);
    createdCount = 0;
}

void MemFS::writeToFile(int numFiles, const std::vector<std::pair<std::string, std::string>>& fileData) {
    for (const auto& [filename, data] : fileData)
        writeFile(filename, data);
}

void MemFS::deleteFiles(int numFiles, const std::vector<std::string>& filenames) {
    for (const auto& filename : filenames)
        deleteFile(filename);
}
