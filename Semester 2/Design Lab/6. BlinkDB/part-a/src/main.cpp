/**
 * @file BlinkDB.cpp
 * @brief BlinkDB - A lightweight key-value store with LRU eviction and AOF persistence.
 *
 * This file implements BlinkDB, a simple in-memory key-value database that supports
 * basic operations like SET, GET, and DEL with persistence via an append-only file (AOF).
 * It uses an LRU eviction policy when the cache reaches its capacity.
 */

#include <iostream>
#include <unordered_map>
#include <list>
#include <fstream>
#include <sstream>

using namespace std;

/**
 * @class BlinkDB
 * @brief Implements a simple key-value store with LRU eviction and AOF persistence.
 */
class BlinkDB
{
private:
    size_t capacity;                                                      ///< Maximum number of key-value pairs that can be stored in memory.
    unordered_map<string, pair<string, list<string>::iterator>> kv_store; ///< In-memory key-value store.
    list<string> lru_order;                                               ///< Maintains LRU ordering of keys.
    const string filename = "blinkdb.aof";                                ///< Name of the AOF persistence file.

public:
    /**
     * @brief Constructor that initializes the database with a given capacity.
     * @param cap The maximum number of entries allowed in memory (default: 100).
     */
    BlinkDB(size_t cap = 100) : capacity(cap)
    {
        remove(filename.c_str());
    }

    /**
     * @brief Destructor that ensures clean-up of resources.
     */
    ~BlinkDB()
    {
        remove(filename.c_str());
    }

    /**
     * @brief Sets a key-value pair in the database.
     * @param key The key to store.
     * @param value The value associated with the key.
     */
    void set(const string &key, const string &value)
    {
        if (kv_store.find(key) != kv_store.end())
        {
            kv_store[key].first = value;
            lru_order.erase(kv_store[key].second);
        }
        else if (kv_store.size() >= capacity)
        {
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
     * @param key The key to retrieve.
     * @return The value associated with the key, or "NULL" if the key is not found.
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
        if (kv_store.find(key) != kv_store.end())
        {
            lru_order.erase(kv_store[key].second);
            kv_store.erase(key);
            appendToFile("DEL " + key);
        }
        else
        {
            cout << "Does not exist." << endl;
        }
    }

    /**
     * @brief Runs a simple REPL (Read-Eval-Print Loop) for BlinkDB.
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
            string command, key, value;
            ss >> command >> key;

            string extra;
            if (command == "SET")
            {
                ss.ignore();
                getline(ss, value);
                if (value.empty())
                {
                    cout << "Error: SET requires a key and a value.\n";
                    continue;
                }
            }
            else if (command == "GET" || command == "DEL")
            {
                if (ss >> extra)
                {
                    cout << "Error: " << command << " requires only a key.\n";
                    continue;
                }
            }
            else
            {
                cout << "Error: Invalid command.\n";
                continue;
            }

            if (command == "SET")
                set(key, value);
            else if (command == "GET")
                cout << get(key) << endl;
            else if (command == "DEL")
                del(key);
        }
    }

private:
    /**
     * @brief Appends a command to the append-only file (AOF) for persistence.
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
     * @brief Loads a key's value from disk if not found in memory.
     * @param key The key to retrieve.
     * @return The value if found on disk, otherwise "NULL".
     */
    string loadFromDisk(const string &key)
    {
        ifstream file(filename);
        string line, cmd, stored_key, stored_value;
        string last_value;
        bool found = false;
        bool deleted = false;

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

        if (found && !deleted)
        {
            lru_order.push_front(key);
            kv_store[key] = {last_value, lru_order.begin()};
            return last_value;
        }
        return "NULL";
    }

    /**
     * @brief Marks a key as flushed when evicted due to capacity constraints.
     * @param key The key being evicted.
     */
    void flushToDisk(const string &key)
    {
        appendToFile("FLUSH " + key);
    }
};

/**
 * @brief Main function that initializes the database and starts the REPL.
 * @return Program exit status.
 */
int main()
{
    BlinkDB db(5);
    db.runREPL();
    return 0;
}
