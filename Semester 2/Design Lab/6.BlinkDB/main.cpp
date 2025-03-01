#include <iostream>
#include <unordered_map>
#include <list>
#include <fstream>
#include <sstream>

using namespace std;

class BlinkDB
{
private:
    size_t capacity; // Maximum in-memory capacity
    unordered_map<string, pair<string, list<string>::iterator>> kv_store;
    list<string> lru_order;                // LRU order list
    const string filename = "blinkdb.aof"; // Persistence file

public:
    BlinkDB(size_t cap = 100) : capacity(cap)
    {
        loadFromFile(); // Load data from disk on startup
    }

    void set(const string &key, const string &value)
    {
        // If key exists, update value and move to front
        if (kv_store.find(key) != kv_store.end())
        {
            kv_store[key].first = value;
            lru_order.erase(kv_store[key].second);
        }
        // If at capacity, evict LRU key
        else if (kv_store.size() >= capacity)
        {
            string lru_key = lru_order.back();
            lru_order.pop_back();
            kv_store.erase(lru_key);
            flushToDisk(lru_key); // Write evicted key to disk
        }
        // Insert key-value pair
        lru_order.push_front(key);
        kv_store[key] = {value, lru_order.begin()};
        appendToFile("SET " + key + " " + value); // Save operation to log
    }

    string get(const string &key)
    {
        if (kv_store.find(key) != kv_store.end())
        {
            // Move key to front (most recently used)
            lru_order.erase(kv_store[key].second);
            lru_order.push_front(key);
            kv_store[key].second = lru_order.begin();
            return kv_store[key].first;
        }

        // Try retrieving from disk if not found in memory
        return loadFromDisk(key);
    }

    void del(const string &key)
    {
        if (kv_store.find(key) != kv_store.end())
        {
            lru_order.erase(kv_store[key].second);
            kv_store.erase(key);
            appendToFile("DEL " + key); // Log deletion
        }
        else
        {
            cout << "Does not exist." << endl;
        }
    }

    void runREPL()
    {
        string input;
        cout << "BLINK DB Started. Enter commands (SET, GET, DEL)." << endl;

        while (true)
        {
            cout << "User> ";
            getline(cin, input);
            if (input.empty())
                continue;

            stringstream ss(input);
            string command, key, value;
            ss >> command >> key;

            // Count remaining arguments
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
                { // If more than 2 tokens, it's an error
                    cout << "Error: " << command << " requires only a key.\n";
                    continue;
                }
            }
            else
            {
                cout << "Error: Invalid command.\n";
                continue;
            }

            // Execute commands
            if (command == "SET")
            {
                set(key, value);
            }
            else if (command == "GET")
            {
                cout << get(key) << endl;
            }
            else if (command == "DEL")
            {
                del(key);
            }
        }
    }

private:
    void appendToFile(const string &command)
    {
        ofstream file(filename, ios::app);
        if (file.is_open())
        {
            file << command << endl;
            file.close();
        }
    }

    string loadFromDisk(const string &key)
    {
        ifstream file(filename);
        string line, cmd, stored_key, stored_value;

        if (!file.is_open())
            return "NULL";

        while (getline(file, line))
        {
            stringstream ss(line);
            ss >> cmd >> stored_key;
            if (cmd == "SET")
            {
                ss.ignore();
                getline(ss, stored_value);
                if (stored_key == key)
                {
                    file.close();
                    set(stored_key, stored_value); // Load back into memory
                    return stored_value;
                }
            }
            else if (cmd == "DEL" && stored_key == key)
            {
                file.close();
                return "NULL"; // Key was deleted
            }
        }

        file.close();
        return "NULL"; // Key not found
    }

    void loadFromFile()
    {
        ifstream file(filename);
        if (!file.is_open())
            return;

        string line, cmd, stored_key, stored_value;
        while (getline(file, line))
        {
            stringstream ss(line);
            ss >> cmd >> stored_key;
            if (cmd == "SET")
            {
                ss.ignore();
                getline(ss, stored_value);
                set(stored_key, stored_value);
            }
            else if (cmd == "DEL")
            {
                del(stored_key);
            }
        }
        file.close();
    }

    void flushToDisk(const string &key)
    {
        appendToFile("FLUSH " + key);
    }
};

int main()
{
    BlinkDB db(5); // Small capacity for testing eviction
    db.runREPL();
    return 0;
}
