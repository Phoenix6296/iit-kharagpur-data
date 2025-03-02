#include <iostream>
#include <unordered_map>
#include <list>
#include <fstream>
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
        loadFromFile();
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

            appendToFile("FLUSH " + lru_key);
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
        return "NULL";
    }

    void del(const string &key)
    {
        if (kv_store.find(key) != kv_store.end())
        {
            lru_order.erase(kv_store[key].second);
            kv_store.erase(key);
            appendToFile("DEL " + key);
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
            string command, key, value, extra;
            ss >> command >> key;

            if (command == "SET")
            {
                ss.ignore();
                getline(ss, value);
                if (value.empty())
                {
                    cout << "Error: SET requires a key and a value.\n";
                    continue;
                }
                set(key, value);
            }
            else if (command == "GET")
            {
                if (ss >> extra)
                {
                    cout << "Error: GET requires only a key.\n";
                    continue;
                }
                cout << get(key) << endl;
            }
            else if (command == "DEL")
            {
                if (ss >> extra)
                {
                    cout << "Error: DEL requires only a key.\n";
                    continue;
                }
                del(key);
            }
            else
            {
                cout << "Error: Invalid command.\n";
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
                kv_store[stored_key] = {stored_value, lru_order.insert(lru_order.begin(), stored_key)};
            }
            else if (cmd == "DEL")
                kv_store.erase(stored_key);
        }
        file.close();
    }
};

int main()
{
    BlinkDB db(5);
    db.runREPL();
    return 0;
}
