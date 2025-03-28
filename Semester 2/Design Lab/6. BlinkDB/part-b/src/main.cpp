/**
 * @file BlinkServer.cpp
 * @brief A simple in-memory key-value server using the Redis RESP-2 protocol and kqueue.
 *
 * This file implements a server that accepts multiple client connections and processes
 * SET, GET, and DEL commands via the Redis RESP-2 protocol. It uses kqueue (available on macOS/BSD)
 * for asynchronous event handling and a simple in-memory storage engine for data persistence.
 */

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

#define PORT 9001        ///< The default port on which BlinkDB server listens.
#define MAX_EVENTS 1024  ///< Maximum number of kqueue events to handle at once.
#define BUFFER_SIZE 4096 ///< Size of the read/write buffer in bytes.

/**
 * @class BlinkDB
 * @brief A simple in-memory key-value store with basic persistence.
 *
 * BlinkDB provides thread-safe operations for setting, getting, and deleting keys.
 * It writes all operations to an append-only file (AOF) for durability.
 */
class BlinkDB
{
private:
    unordered_map<string, string> kv_store; ///< Internal in-memory key-value map.
    const string filename = "blinkdb.aof";  ///< Name of the append-only file for persistence.
    mutex db_mutex;                         ///< Mutex to ensure thread-safe operations.

public:
    /**
     * @brief Constructor that clears any existing AOF file.
     *
     * Removes the AOF file at startup to simulate a fresh database instance.
     */
    BlinkDB() { remove(filename.c_str()); }

    /**
     * @brief Destructor that removes the AOF file upon shutdown.
     */
    ~BlinkDB() { remove(filename.c_str()); }

    /**
     * @brief Stores a key-value pair in the database.
     * @param key The key to store.
     * @param value The value associated with the key.
     *
     * This operation is thread-safe. It updates the in-memory store and appends
     * the corresponding "SET" command to the AOF file for persistence.
     */
    void set(const string &key, const string &value)
    {
        lock_guard<mutex> lock(db_mutex);
        kv_store[key] = value;
        appendToFile("SET " + key + " " + value);
    }

    /**
     * @brief Retrieves the value associated with a key.
     * @param key The key to retrieve.
     * @return The value associated with the key, or an empty string if the key is not found.
     *
     * This function is thread-safe and looks up the value in the in-memory store.
     */
    string get(const string &key)
    {
        lock_guard<mutex> lock(db_mutex);
        auto it = kv_store.find(key);
        return it != kv_store.end() ? it->second : "";
    }

    /**
     * @brief Deletes a key-value pair from the database.
     * @param key The key to delete.
     *
     * If the key exists in the in-memory store, it is removed and the deletion command
     * ("DEL") is appended to the AOF file for persistence.
     */
    bool del(const string &key)
    {
        lock_guard<mutex> lock(db_mutex);
        if (kv_store.find(key) != kv_store.end())
        {
            kv_store.erase(key);
            appendToFile("DEL " + key);
            return true;
        }
        return false;
    }

private:
    /**
     * @brief Appends a command to the AOF file for persistence.
     * @param command The command string to append (e.g., "SET key value").
     *
     * Opens the AOF file in append mode and writes the command. No error handling is performed.
     */
    void appendToFile(const string &command)
    {
        ofstream file(filename, ios::app);
        if (file.is_open())
        {
            file << command << endl;
        }
    }
};

/**
 * @brief Parses a Redis RESP-2 formatted string into command tokens.
 * @param input The RESP-2 formatted input string from the client.
 * @return A pair consisting of:
 *         - A vector of parsed tokens (strings).
 *         - The number of bytes successfully parsed.
 *
 * The function processes the input string according to the RESP-2 protocol.
 * If the input is invalid or incomplete, it returns an empty vector and a parsed length of 0.
 */
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

/**
 * @struct ClientState
 * @brief Maintains the read and write buffers for a connected client.
 *
 * This structure stores the state for a client connection including the socket file descriptor,
 * a buffer for incoming data (read_buffer), and a buffer for outgoing data (write_buffer).
 */
struct ClientState
{
    int fd;              ///< File descriptor for the client's socket.
    string read_buffer;  ///< Buffer to store data read from the client.
    string write_buffer; ///< Buffer to store data to be written to the client.
};

/**
 * @class BlinkServer
 * @brief Implements a TCP server that handles multiple client connections using kqueue.
 *
 * BlinkServer listens on a specified port and accepts incoming client connections.
 * It processes commands encoded in the Redis RESP-2 protocol (SET, GET, DEL) by
 * interacting with an internal BlinkDB instance. The server uses kqueue for asynchronous
 * event handling.
 */
class BlinkServer
{
    int server_fd;                           ///< Server socket file descriptor.
    int kq;                                  ///< kqueue descriptor.
    BlinkDB db;                              ///< Internal key-value store.
    unordered_map<int, ClientState> clients; ///< Maps client socket file descriptors to their state.

public:
    /**
     * @brief Default constructor initializes server file descriptor and kqueue descriptor.
     */
    BlinkServer() : server_fd(-1), kq(-1) {}

    /**
     * @brief Starts the server.
     *
     * This function sets up the server socket, initializes kqueue, and enters the main event loop.
     */
    void run()
    {
        setupServer();
        setupKqueue();
        eventLoop();
    }

private:
    /**
     * @brief Creates and binds the server socket, then begins listening for connections.
     *
     * This function sets the socket options, binds to the specified port, and starts listening.
     * It also marks the socket as non-blocking.
     *
     * @throws runtime_error if the socket, bind, or listen operation fails.
     */
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

        if (::bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
            throw runtime_error("bind failed");

        if (listen(server_fd, MAX_EVENTS) < 0)
            throw runtime_error("listen failed");

        fcntl(server_fd, F_SETFL, O_NONBLOCK);
        cout << "BlinkDB Server started on port " << PORT << endl;
    }

    /**
     * @brief Initializes kqueue and registers the server socket for read events.
     *
     * @throws runtime_error if kqueue initialization fails.
     */
    void setupKqueue()
    {
        kq = kqueue();
        if (kq == -1)
            throw runtime_error("kqueue failed");

        struct kevent ev;
        EV_SET(&ev, server_fd, EVFILT_READ, EV_ADD, 0, 0, NULL);
        kevent(kq, &ev, 1, NULL, 0, NULL);
    }

    /**
     * @brief Main event loop that waits for kqueue events and processes them.
     *
     * This function continuously waits for events. When a new event occurs, it determines
     * if it is a new connection or an event from an existing client and dispatches accordingly.
     */
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

    /**
     * @brief Accepts a new client connection and registers it with kqueue.
     *
     * The new client socket is set to non-blocking mode and added to the kqueue for read events.
     */
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

        // Initialize a new ClientState for the accepted client.
        clients[client_fd] = {client_fd, "", ""};
    }

    /**
     * @brief Handles events from a client.
     * @param fd The file descriptor of the client.
     *
     * This function reads incoming data from the client, appends it to the client's read buffer,
     * processes complete commands, and sends out responses.
     */
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

    /**
     * @brief Processes complete RESP-2 commands from a client's read buffer.
     * @param client The client state containing the read and write buffers.
     *
     * Parses the read buffer for complete commands using the RESP-2 protocol,
     * processes each command, and appends the response to the client's write buffer.
     */
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

            // Remove the processed command from the read buffer.
            client.read_buffer.erase(0, parsed);
        }

        if (!client.write_buffer.empty())
        {
            sendResponse(client);
        }
    }

    /**
     * @brief Processes a single RESP-2 command and generates a response.
     * @param tokens A vector of command tokens (e.g., {"SET", "key", "value"}).
     * @param response The generated response to be sent back to the client.
     *
     * This function validates the command and calls the corresponding operation on the BlinkDB instance.
     * Supported commands are SET, GET, and DEL.
     */
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
            response = value.empty()
                           ? "$-1\r\n" // Key not found
                           : "$" + to_string(value.size()) + "\r\n" + value + "\r\n";
        }
        else if (cmd == "DEL" && tokens.size() == 2)
        {
            bool deleted = db.del(tokens[1]);         // Check if key was deleted
            response = deleted ? ":1\r\n" : ":0\r\n"; // Correct response for DEL
        }
        else
        {
            response = "-ERR unknown command\r\n";
        }
    }

    /**
     * @brief Sends pending data from the client's write buffer to the client.
     * @param client The client state containing the write buffer.
     *
     * The function attempts to send as much data as possible. If the send fails due to an error
     * (other than EAGAIN), the connection is closed.
     */
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

    /**
     * @brief Closes the connection for a client and removes it from the active clients map.
     * @param fd The file descriptor of the client to close.
     */
    void closeConnection(int fd)
    {
        close(fd);
        clients.erase(fd);
    }
};

/**
 * @brief Main entry point of the BlinkServer application.
 * @return Exit status of the program (0 for success, 1 for failure).
 *
 * The main function creates a BlinkServer instance and starts it.
 * Any exceptions encountered during server startup or operation are caught,
 * and an error message is printed.
 */
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
