#ifndef MEMFS_H
#define MEMFS_H

#include <string>
#include <unordered_map>
#include <mutex>
#include <vector>
#include <ctime>
#include <atomic>

// Structure to hold file metadata
struct File {
    std::string content;
    std::time_t created;
    std::time_t lastModified;

    File() : created(std::time(nullptr)), lastModified(std::time(nullptr)) {}
};

// Global file system map for the external functions
extern std::unordered_map<std::string, File> memFS;
extern std::mutex fsMutex;

// External function declarations (non-class-based API)
void createFiles(int numFiles, const std::vector<std::string>& filenames);
void writeToFile(const std::vector<std::pair<std::string, std::string>>& fileContentPairs);
void deleteFile(const std::string& filename);
void readFile(const std::string& filename);
void listFiles(bool detailed);

// Class-based API for the in-memory file system
class MemFS {
private:
    struct FileMetadata {
        std::string content;
        size_t size;
        std::string creationDate;
        std::string lastModified;
    };

    std::unordered_map<std::string, FileMetadata> files;
    std::mutex fsMutex;
    std::atomic<int> createdCount{0};

    // Private helper functions
    std::string getCurrentDate() const;
    void createFile(const std::string &filename);
    void writeFile(const std::string &filename, const std::string &data);
    void deleteFile(const std::string &filename);

public:
    // Class-based functions for bulk operations
    void createFiles(int numFiles, const std::vector<std::string>& filenames);
    void writeToFile(int numFiles, const std::vector<std::pair<std::string, std::string>>& fileData);
    void deleteFiles(int numFiles, const std::vector<std::string>& filenames);
};

#endif // MEMFS_H
