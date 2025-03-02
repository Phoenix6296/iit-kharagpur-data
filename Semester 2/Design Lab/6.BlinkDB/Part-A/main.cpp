#include <iostream>
#include <unordered_map>
#include <list>
#include <fstream>
#include <cstdlib>
#include <sstream>

using namespace std;

class BlinkDB
{
private:
    size_t capacity;
    unordered_map<string, pair<string, list<string>::iterator>> kv_store;
    list<string> lru_order;
    const string filename = "blinkdb.aof";

public:
    BlinkDB(size_t cap = 100) : capacity(cap)
    {
        remove(filename.c_str());
        loadFromFile();
        atexit(deleteAOF);
    }

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
                    set(stored_key, stored_value);
                    return stored_value;
                }
            }
            else if (cmd == "DEL" && stored_key == key)
            {
                file.close();
                return "NULL";
            }
        }
        file.close();
        return "NULL";
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

    static void deleteAOF()
    {
        remove("blinkdb.aof");
    }
};

int main()
{
    BlinkDB db(5);
    db.runREPL();
    return 0;
}
