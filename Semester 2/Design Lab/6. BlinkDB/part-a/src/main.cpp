/**
 * @file BlinkDB.cpp
 * @brief BlinkDB - A lightweight key-value store with LRU eviction, AOF persistence, and parallel processing.
 *
 * This file implements BlinkDB, a simple in-memory key-value database that supports
 * basic operations like SET, GET, and DEL with persistence via an append-only file (AOF).
 * It uses an LRU eviction policy when the cache reaches its capacity and processes commands
 * concurrently using a thread pool.
 */

#include <iostream>
#include <unordered_map>
#include <list>
#include <fstream>
#include <sstream>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <future>
#include <vector>
#include <cstdio>

using namespace std;

/**
 * @struct Command
 * @brief Structure to represent a database command for parallel processing.
 *
 * This structure holds the details of a command that will be processed
 * by one of the worker threads. For GET commands, a promise is used to return
 * the result asynchronously.
 */
struct Command
{
    string type;                    ///< The type of command (e.g., "SET", "GET", "DEL").
    string key;                     ///< The key involved in the command.
    string value;                   ///< The value associated with the key (for SET commands).
    promise<string> *resultPromise; ///< Pointer to a promise for returning the result of GET commands. For SET and DEL commands, this is nullptr.
};

/**
 * @class BlinkDB
 * @brief A lightweight key-value store with LRU eviction, AOF persistence, and parallel processing.
 *
 * BlinkDB stores key-value pairs in memory with a fixed capacity. When the cache is full,
 * the least recently used (LRU) key is evicted. All operations are logged to an append-only file (AOF)
 * for persistence. Commands are processed concurrently using a fixed-size thread pool.
 */
class BlinkDB
{
private:
    size_t capacity; ///< Maximum number of key-value pairs stored in memory.

    /// In-memory key-value store where each key is mapped to a pair containing the value and an iterator to its LRU list position.
    unordered_map<string, pair<string, list<string>::iterator>> kv_store;

    list<string> lru_order; ///< Maintains keys in order of most-recently used (front) to least-recently used (back).

    const string filename = "blinkdb.aof"; ///< Name of the append-only file used for persistence.

    mutex db_mutex;   ///< Mutex to protect concurrent access to the key-value store and LRU list.
    mutex file_mutex; ///< Mutex to protect file I/O operations.

    queue<Command> commandQueue; ///< Queue of commands to be processed by worker threads.
    mutex queueMutex;            ///< Mutex to protect access to the command queue.
    condition_variable cv;       ///< Condition variable to notify worker threads when a new command is available.
    bool stop;                   ///< Flag to signal worker threads to stop processing commands.
    vector<thread> workers;      ///< Vector of worker threads processing commands.

    const size_t numWorkers = 4; ///< Number of worker threads.

public:
    /**
     * @brief Constructs a BlinkDB instance with a given capacity.
     * @param cap The maximum number of entries allowed in memory (default is 100).
     *
     * The constructor removes any existing AOF file and launches the worker threads
     * that will process commands concurrently.
     */
    BlinkDB(size_t cap = 100) : capacity(cap), stop(false)
    {
        // Remove any existing AOF file to start fresh.
        remove(filename.c_str());

        // Launch worker threads.
        for (size_t i = 0; i < numWorkers; ++i)
        {
            workers.emplace_back(&BlinkDB::workerThread, this);
        }
    }

    /**
     * @brief Destroys the BlinkDB instance and cleans up resources.
     *
     * Signals worker threads to stop, waits for them to join, and removes the AOF file.
     */
    ~BlinkDB()
    {
        {
            // Signal all worker threads to stop processing commands.
            unique_lock<mutex> lock(queueMutex);
            stop = true;
        }
        cv.notify_all();

        // Join all worker threads.
        for (auto &worker : workers)
        {
            if (worker.joinable())
                worker.join();
        }
        // Optionally remove the AOF file on shutdown.
        remove(filename.c_str());
    }

    /**
     * @brief Sets a key-value pair in the database.
     * @param key The key to store.
     * @param value The value to associate with the key.
     *
     * If the key already exists, its value is updated and its position in the LRU list is refreshed.
     * If the database reaches its capacity, the least recently used key is evicted and flushed to disk.
     * The command is appended to the AOF file for persistence.
     */
    void set(const string &key, const string &value)
    {
        lock_guard<mutex> lock(db_mutex);
        if (kv_store.find(key) != kv_store.end())
        {
            // Update existing key.
            kv_store[key].first = value;
            lru_order.erase(kv_store[key].second);
        }
        else if (kv_store.size() >= capacity)
        {
            // Evict the least recently used key.
            string lru_key = lru_order.back();
            lru_order.pop_back();
            kv_store.erase(lru_key);
            flushToDisk(lru_key);
        }
        // Insert/update key and update LRU order.
        lru_order.push_front(key);
        kv_store[key] = {value, lru_order.begin()};
        appendToFile("SET " + key + " " + value);
    }

    /**
     * @brief Retrieves the value associated with a key.
     * @param key The key to look up.
     * @return The value associated with the key, or "NULL" if the key does not exist.
     *
     * The function first checks the in-memory cache. If the key is not found,
     * it attempts to load the value from disk.
     */
    string get(const string &key)
    {
        {
            lock_guard<mutex> lock(db_mutex);
            if (kv_store.find(key) != kv_store.end())
            {
                // Refresh the key's position in the LRU list.
                lru_order.erase(kv_store[key].second);
                lru_order.push_front(key);
                kv_store[key].second = lru_order.begin();
                return kv_store[key].first;
            }
        }
        // Key not found in memory; attempt to load from disk.
        return loadFromDisk(key);
    }

    /**
     * @brief Deletes a key-value pair from the database.
     * @param key The key to delete.
     *
     * If the key exists in memory, it is removed from both the key-value store and the LRU list.
     * The delete operation is logged in the AOF file.
     */
    void del(const string &key)
    {
        bool keyFound = false;
        {
            // First, check if the key exists in memory.
            lock_guard<mutex> lock(db_mutex);
            if (kv_store.find(key) != kv_store.end())
            {
                keyFound = true;
            }
        }
        if (!keyFound)
        {
            // If the key isn’t in memory, try loading it from disk.
            // Note: loadFromDisk() will load the key into memory if found.
            string value = loadFromDisk(key);
            if (value == "NULL")
            {
                cout << "Does not exist." << endl;
                return;
            }
        }
        {
            // Now that the key is either already in memory or loaded from disk,
            // delete it from the in-memory store.
            lock_guard<mutex> lock(db_mutex);
            if (kv_store.find(key) != kv_store.end())
            {
                lru_order.erase(kv_store[key].second);
                kv_store.erase(key);
            }
        }
        // Log the deletion in the AOF.
        appendToFile("DEL " + key);
    }

    /**
     * @brief Runs a simple Read-Eval-Print Loop (REPL) for interacting with BlinkDB.
     *
     * The REPL accepts commands (SET, GET, DEL, EXIT) from the user, enqueues them for
     * parallel processing by worker threads, and outputs the results of GET commands.
     */
    void runREPL()
    {
        string input;
        cout << "BLINK DB Started. Enter commands (SET, GET, DEL, EXIT)." << endl;

        while (true)
        {
            cout << "User> ";
            getline(cin, input);
            if (input.empty())
                continue;

            if (input == "EXIT")
            {
                cout << "Exiting BLINK DB..." << endl;
                break;
            }

            stringstream ss(input);
            string commandType, key, value;
            ss >> commandType >> key;

            // Check for extra input and validate command format.
            string extra;
            if (commandType == "SET")
            {
                ss.ignore();
                getline(ss, value);
                if (value.empty())
                {
                    cout << "Error: SET requires a key and a value." << endl;
                    continue;
                }
            }
            else if (commandType == "GET" || commandType == "DEL")
            {
                if (ss >> extra)
                {
                    cout << "Error: " << commandType << " requires only a key." << endl;
                    continue;
                }
            }
            else
            {
                cout << "Error: Invalid command." << endl;
                continue;
            }

            // Prepare a command.
            Command cmd;
            cmd.type = commandType;
            cmd.key = key;
            cmd.value = value;
            cmd.resultPromise = nullptr;

            // For GET commands, create a promise to capture the result.
            future<string> resultFuture;
            if (commandType == "GET")
            {
                promise<string> *prom = new promise<string>;
                resultFuture = prom->get_future();
                cmd.resultPromise = prom;
            }

            // Enqueue the command.
            {
                lock_guard<mutex> lock(queueMutex);
                commandQueue.push(cmd);
            }
            cv.notify_one();

            // For GET commands, wait for the result and then print it.
            if (commandType == "GET")
            {
                string result = resultFuture.get();
                cout << result << endl;
            }
        }

        // Signal worker threads to exit.
        {
            lock_guard<mutex> lock(queueMutex);
            stop = true;
        }
        cv.notify_all();
    }

private:
    /**
     * @brief The worker thread function that processes commands from the command queue.
     *
     * Worker threads continuously wait for commands to be available in the queue. Once a command
     * is dequeued, it is processed by calling the corresponding operation (SET, GET, or DEL).
     */
    void workerThread()
    {
        while (true)
        {
            Command cmd;
            {
                unique_lock<mutex> lock(queueMutex);
                cv.wait(lock, [this]
                        { return !commandQueue.empty() || stop; });
                if (stop && commandQueue.empty())
                    return;
                cmd = commandQueue.front();
                commandQueue.pop();
            }
            // Process the command based on its type.
            if (cmd.type == "SET")
            {
                set(cmd.key, cmd.value);
            }
            else if (cmd.type == "GET")
            {
                string result = get(cmd.key);
                if (cmd.resultPromise)
                {
                    cmd.resultPromise->set_value(result);
                    delete cmd.resultPromise;
                }
            }
            else if (cmd.type == "DEL")
            {
                del(cmd.key);
            }
        }
    }

    /**
     * @brief Appends a command string to the append-only file (AOF) for persistence.
     * @param command The command string to append (e.g., "SET key value").
     *
     * This function acquires a lock on the file mutex to ensure thread-safe writes.
     */
    void appendToFile(const string &command)
    {
        lock_guard<mutex> lock(file_mutex);
        ofstream file(filename, ios::app);
        if (file.is_open())
        {
            file << command << endl;
            file.close();
        }
    }

    /**
     * @brief Loads a key's value from disk if it is not present in memory.
     * @param key The key to retrieve.
     * @return The value associated with the key if found on disk; otherwise, returns "NULL".
     *
     * The function reads through the AOF file to find the latest SET or DEL command
     * for the given key. If the key was set and not subsequently deleted, it is reloaded into
     * memory and returned.
     */
    string loadFromDisk(const string &key)
    {
        string last_value;
        bool found = false;
        bool deleted = false;

        // Read the AOF file while holding the file lock.
        {
            lock_guard<mutex> fileLock(file_mutex);
            ifstream file(filename);
            string line, cmd, stored_key, stored_value;

            if (!file.is_open())
                return "NULL";

            while (getline(file, line))
            {
                stringstream ss(line);
                ss >> cmd >> stored_key;
                if (stored_key == key)
                {
                    if (cmd == "SET")
                    {
                        ss.ignore();
                        getline(ss, stored_value);
                        last_value = stored_value;
                        found = true;
                        deleted = false;
                    }
                    else if (cmd == "DEL")
                    {
                        found = true;
                        deleted = true;
                    }
                }
            }
            file.close();
        } // End of fileLock scope.

        if (found && !deleted)
        {
            // Load the key into memory.
            {
                lock_guard<mutex> lock(db_mutex);
                if (kv_store.size() >= capacity)
                {
                    // Evict the least recently used key if at capacity.
                    string evict_key = lru_order.back();
                    lru_order.pop_back();
                    kv_store.erase(evict_key);
                    flushToDisk(evict_key);
                }
                // Insert the reloaded key.
                lru_order.push_front(key);
                kv_store[key] = {last_value, lru_order.begin()};
            }
            return last_value;
        }
        return "NULL";
    }

    /**
     * @brief Flushes a key to disk when it is evicted from the in-memory cache.
     * @param key The key being evicted.
     *
     * This function logs the eviction by appending a "FLUSH" command to the AOF file.
     */
    void flushToDisk(const string &key)
    {
        appendToFile("FLUSH " + key);
    }
};

/**
 * @brief The main function that initializes BlinkDB and starts the REPL.
 * @return Exit status of the program.
 *
 * Creates an instance of BlinkDB with a specified capacity and then starts a REPL
 * that accepts user commands.
 */
int main()
{
    // Create a BlinkDB instance with a capacity of 5.
    BlinkDB db(3);
    db.runREPL();
    return 0;
}
