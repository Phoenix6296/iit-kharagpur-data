/**
 * @file BlinkDB.cpp
 * @brief BlinkDB - A lightweight key-value store with LRU eviction and AOF persistence (single-threaded).
 */

#include <iostream>
#include <unordered_map>
#include <list>
#include <fstream>
#include <sstream>
#include <cstdio>

using namespace std;

/**
 * @class BlinkDB
 * @brief A lightweight single-threaded key-value store with LRU eviction and AOF persistence.
 *
 * BlinkDB stores key-value pairs in memory with a fixed capacity. When the cache is full,
 * the least recently used (LRU) key is evicted. All operations are logged to an
 * append-only file (AOF) for persistence.
 */
class BlinkDB
{
private:
    size_t capacity;                                                      ///< Maximum number of key-value pairs stored in memory.
    unordered_map<string, pair<string, list<string>::iterator>> kv_store; ///< Key-value storage with iterators to LRU list.
    list<string> lru_order;                                               ///< Keys in LRU order (most recently used at front).

    const string filename = "blinkdb.aof"; ///< Append-only file for persistence.

public:
    /**
     * @brief Constructs a BlinkDB instance with a given capacity.
     * @param cap The maximum number of entries allowed in memory (default is 100).
     */
    BlinkDB(size_t cap = 100) : capacity(cap)
    {
        remove(filename.c_str()); // Start fresh by removing existing AOF file
    }

    /**
     * @brief Destroys the BlinkDB instance and cleans up resources.
     *
     * Removes the AOF file on destruction.
     */
    ~BlinkDB()
    {
        remove(filename.c_str());
    }

    /**
     * @brief Sets a key-value pair in the database.
     * @param key The key to set.
     * @param value The value to associate with the key.
     */
    void set(const string &key, const string &value)
    {
        if (kv_store.find(key) != kv_store.end())
        {
            // Update existing key
            kv_store[key].first = value;
            lru_order.erase(kv_store[key].second);
        }
        else if (kv_store.size() >= capacity)
        {
            // Evict least recently used key
            string lru_key = lru_order.back();
            lru_order.pop_back();
            kv_store.erase(lru_key);
            flushToDisk(lru_key);
        }
        lru_order.push_front(key);
        kv_store[key] = {value, lru_order.begin()};
        appendToFile("SET " + key + " " + value);
    }

    /**
     * @brief Retrieves the value associated with a key.
     * @param key The key to look up.
     * @return The value associated with the key, or "NULL" if not found.
     */
    string get(const string &key)
    {
        if (kv_store.find(key) != kv_store.end())
        {
            lru_order.erase(kv_store[key].second);
            lru_order.push_front(key);
            kv_store[key].second = lru_order.begin();
            return kv_store[key].first;
        }
        return loadFromDisk(key);
    }

    /**
     * @brief Deletes a key-value pair from the database.
     * @param key The key to delete.
     */
    void del(const string &key)
    {
        if (kv_store.find(key) == kv_store.end())
        {
            if (loadFromDisk(key) == "NULL")
            {
                cout << "Does not exist." << endl;
                return;
            }
        }

        if (kv_store.find(key) != kv_store.end())
        {
            lru_order.erase(kv_store[key].second);
            kv_store.erase(key);
        }
        appendToFile("DEL " + key);
    }

    /**
     * @brief Runs a simple REPL (Read-Eval-Print Loop) for interacting with BlinkDB.
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
                set(key, value);
            }
            else if (commandType == "GET")
            {
                if (ss >> extra)
                {
                    cout << "Error: GET requires only a key." << endl;
                    continue;
                }
                cout << get(key) << endl;
            }
            else if (commandType == "DEL")
            {
                if (ss >> extra)
                {
                    cout << "Error: DEL requires only a key." << endl;
                    continue;
                }
                del(key);
            }
            else
            {
                cout << "Error: Invalid command." << endl;
            }
        }
    }

private:
    /**
     * @brief Appends a command to the append-only file.
     * @param command The command to append.
     */
    void appendToFile(const string &command)
    {
        ofstream file(filename, ios::app);
        if (file.is_open())
        {
            file << command << endl;
            file.close();
        }
    }

    /**
     * @brief Loads a key from the AOF file.
     * @param key The key to search for.
     * @return The associated value if found, or "NULL" otherwise.
     */
    string loadFromDisk(const string &key)
    {
        string last_value;
        bool found = false;
        bool deleted = false;

        ifstream file(filename);
        if (!file.is_open())
            return "NULL";

        string line, cmd, stored_key, stored_value;
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

        if (found && !deleted)
        {
            if (kv_store.size() >= capacity)
            {
                string evict_key = lru_order.back();
                lru_order.pop_back();
                kv_store.erase(evict_key);
                flushToDisk(evict_key);
            }
            lru_order.push_front(key);
            kv_store[key] = {last_value, lru_order.begin()};
            return last_value;
        }
        return "NULL";
    }

    /**
     * @brief Logs a key eviction to the AOF file.
     * @param key The key that was flushed.
     */
    void flushToDisk(const string &key)
    {
        appendToFile("FLUSH " + key);
    }
};

/**
 * @brief Main function to run BlinkDB.
 */
int main()
{
    BlinkDB db(3); // Example capacity of 3
    db.runREPL();
    return 0;
}
