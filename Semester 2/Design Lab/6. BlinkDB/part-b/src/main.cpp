#include <iostream>
#include <unordered_map>
#include <fstream>
#include <vector>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/event.h>
#include <cstring>
#include <algorithm>
#include <sstream>
#include <mutex>

using namespace std;

#define PORT 9001
#define MAX_EVENTS 1024
#define BUFFER_SIZE 4096

// ----------------------------
// BlinkDB Storage Engine
// ----------------------------
class BlinkDB
{
private:
    unordered_map<string, string> kv_store;
    const string filename = "blinkdb.aof";
    mutex db_mutex;

public:
    BlinkDB() { remove(filename.c_str()); }
    ~BlinkDB() { remove(filename.c_str()); }

    void set(const string &key, const string &value)
    {
        lock_guard<mutex> lock(db_mutex);
        kv_store[key] = value;
        appendToFile("SET " + key + " " + value);
    }

    string get(const string &key)
    {
        lock_guard<mutex> lock(db_mutex);
        auto it = kv_store.find(key);
        return it != kv_store.end() ? it->second : "";
    }

    void del(const string &key)
    {
        lock_guard<mutex> lock(db_mutex);
        if (kv_store.erase(key))
            appendToFile("DEL " + key);
    }

private:
    void appendToFile(const string &command)
    {
        ofstream file(filename, ios::app);
        if (file.is_open())
        {
            file << command << endl;
        }
    }
};

// ----------------------------
// RESP-2 Parser
// ----------------------------
pair<vector<string>, size_t> parseRESP(const string &input)
{
    vector<string> tokens;
    size_t pos = 0;

    if (input.empty() || input[pos] != '*')
        return {tokens, 0};
    pos++;

    int num_args = 0;
    while (pos < input.size() && isdigit(input[pos]))
    {
        num_args = num_args * 10 + (input[pos] - '0');
        pos++;
    }

    if (pos + 1 >= input.size() || input[pos] != '\r' || input[pos + 1] != '\n')
        return {tokens, 0};
    pos += 2;

    for (int i = 0; i < num_args; i++)
    {
        if (pos >= input.size() || input[pos] != '$')
            return {tokens, 0};
        pos++;

        int length = 0;
        while (pos < input.size() && isdigit(input[pos]))
        {
            length = length * 10 + (input[pos] - '0');
            pos++;
        }

        if (pos + 1 >= input.size() || input[pos] != '\r' || input[pos + 1] != '\n')
            return {tokens, 0};
        pos += 2;

        if (pos + length > input.size())
            return {tokens, 0};
        tokens.push_back(input.substr(pos, length));
        pos += length;

        if (pos + 1 >= input.size() || input[pos] != '\r' || input[pos + 1] != '\n')
            return {tokens, 0};
        pos += 2;
    }

    return {tokens, pos};
}

// ----------------------------
// Client Connection State
// ----------------------------
struct ClientState
{
    int fd;
    string read_buffer;
    string write_buffer;
};

// ----------------------------
// TCP Server with kqueue
// ----------------------------
class BlinkServer
{
    int server_fd;
    int kq;
    BlinkDB db;
    unordered_map<int, ClientState> clients;

public:
    BlinkServer() : server_fd(-1), kq(-1) {}

    void run()
    {
        setupServer();
        setupKqueue();
        eventLoop();
    }

private:
    void setupServer()
    {
        server_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (server_fd < 0)
            throw runtime_error("socket failed");

        int opt = 1;
        setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in server_addr{};
        server_addr.sin_family = AF_INET;
        server_addr.sin_addr.s_addr = INADDR_ANY;
        server_addr.sin_port = htons(PORT);

        if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
            throw runtime_error("bind failed");

        if (listen(server_fd, MAX_EVENTS) < 0)
            throw runtime_error("listen failed");

        fcntl(server_fd, F_SETFL, O_NONBLOCK);
        cout << "BlinkDB Server started on port " << PORT << endl;
    }

    void setupKqueue()
    {
        kq = kqueue();
        if (kq == -1)
            throw runtime_error("kqueue failed");

        struct kevent ev;
        EV_SET(&ev, server_fd, EVFILT_READ, EV_ADD, 0, 0, NULL);
        kevent(kq, &ev, 1, NULL, 0, NULL);
    }

    void eventLoop()
    {
        struct kevent events[MAX_EVENTS];

        while (true)
        {
            int nev = kevent(kq, NULL, 0, events, MAX_EVENTS, NULL);
            for (int i = 0; i < nev; i++)
            {
                int fd = events[i].ident;

                if (fd == server_fd)
                {
                    acceptNewConnection();
                }
                else
                {
                    handleClientEvent(fd);
                }
            }
        }
    }

    void acceptNewConnection()
    {
        sockaddr_in client_addr{};
        socklen_t len = sizeof(client_addr);
        int client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &len);
        if (client_fd < 0)
            return;

        fcntl(client_fd, F_SETFL, O_NONBLOCK);

        struct kevent ev;
        EV_SET(&ev, client_fd, EVFILT_READ, EV_ADD | EV_ENABLE, 0, 0, NULL);
        kevent(kq, &ev, 1, NULL, 0, NULL);

        clients[client_fd] = {client_fd, "", ""};
    }

    void handleClientEvent(int fd)
    {
        auto it = clients.find(fd);
        if (it == clients.end())
            return;

        ClientState &client = it->second;
        char buffer[BUFFER_SIZE];

        while (true)
        {
            ssize_t count = recv(fd, buffer, sizeof(buffer), 0);
            if (count > 0)
            {
                client.read_buffer.append(buffer, count);
            }
            else if (count == 0 || (count < 0 && errno != EAGAIN))
            {
                closeConnection(fd);
                return;
            }
            else
            {
                break;
            }
        }

        processClientBuffer(client);
    }

    void processClientBuffer(ClientState &client)
    {
        while (true)
        {
            auto [tokens, parsed] = parseRESP(client.read_buffer);
            if (parsed == 0)
                break;

            string response;
            processCommand(tokens, response);
            client.write_buffer += response;

            client.read_buffer.erase(0, parsed);
        }

        if (!client.write_buffer.empty())
        {
            sendResponse(client);
        }
    }

    void processCommand(const vector<string> &tokens, string &response)
    {
        if (tokens.empty())
        {
            response = "-ERR empty command\r\n";
            return;
        }

        string cmd = tokens[0];
        transform(cmd.begin(), cmd.end(), cmd.begin(), ::toupper);

        if (cmd == "SET" && tokens.size() == 3)
        {
            db.set(tokens[1], tokens[2]);
            response = "+OK\r\n";
        }
        else if (cmd == "GET" && tokens.size() == 2)
        {
            string value = db.get(tokens[1]);
            response = value.empty() ? "$-1\r\n" : "$" + to_string(value.size()) + "\r\n" + value + "\r\n";
        }
        else if (cmd == "DEL" && tokens.size() == 2)
        {
            db.del(tokens[1]);
            response = ":1\r\n";
        }
        else
        {
            response = "-ERR unknown command\r\n";
        }
    }

    void sendResponse(ClientState &client)
    {
        ssize_t sent = send(client.fd, client.write_buffer.data(), client.write_buffer.size(), 0);
        if (sent > 0)
        {
            client.write_buffer.erase(0, sent);
        }
        else if (sent < 0 && errno != EAGAIN)
        {
            closeConnection(client.fd);
        }
    }

    void closeConnection(int fd)
    {
        close(fd);
        clients.erase(fd);
    }
};

// ----------------------------
// Main Function
// ----------------------------
int main()
{
    try
    {
        BlinkServer server;
        server.run();
    }
    catch (const exception &e)
    {
        cerr << "Server error: " << e.what() << endl;
        return 1;
    }
    return 0;
}