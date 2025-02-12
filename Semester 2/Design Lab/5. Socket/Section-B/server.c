#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <time.h>

#define PORT 8081
#define BUFFER_SIZE 1024

pthread_mutex_t log_mutex = PTHREAD_MUTEX_INITIALIZER; // Mutex to synchronize log file access

// Function to log messages to a file with timestamp, client IP, and port
void log_message(const char *client_ip, int client_port, const char *message) {
    FILE *log_file = fopen("log.txt", "a");
    if (log_file == NULL) {
        perror("Error opening log file");
        return;
    }

    // Get the current time
    time_t rawtime;
    struct tm *timeinfo;
    char timestamp[100];

    time(&rawtime);
    timeinfo = localtime(&rawtime);
    strftime(timestamp, 100, "%Y-%m-%d %H:%M:%S", timeinfo);

    // Log the message with the timestamp, client IP, and client port
    fprintf(log_file, "[%s] Client IP: %s, Client Port: %d, Message: %s\n", timestamp, client_ip, client_port, message);

    fclose(log_file);
}

// Function to handle each client connection
void *handle_client(void *arg) {
    int client_fd = *((int *)arg);
    char buffer[BUFFER_SIZE];
    struct sockaddr_in client_addr;
    socklen_t client_addr_len = sizeof(client_addr);

    // Get the client's IP address and port
    getpeername(client_fd, (struct sockaddr *)&client_addr, &client_addr_len);
    char client_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &(client_addr.sin_addr), client_ip, INET_ADDRSTRLEN);
    int client_port = ntohs(client_addr.sin_port);  // Client's port number

    // Receive and process messages from the client
    while (1) {
        memset(buffer, 0, BUFFER_SIZE);
        int bytes_received = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
        if (bytes_received <= 0) {
            if (bytes_received == 0) {
                printf("Client %s:%d disconnected\n", client_ip, client_port);
            } else {
                perror("Receive failed");
            }
            break;
        }

        // Print the message from the client with its IP and port
        printf("Message from client %s:%d: %s\n", client_ip, client_port, buffer);

        // Log the message with the client's information
        pthread_mutex_lock(&log_mutex);
        log_message(client_ip, client_port, buffer);
        pthread_mutex_unlock(&log_mutex);

        // Send acknowledgment to the client
        const char *ack = "Message received";
        send(client_fd, ack, strlen(ack), 0);
    }

    close(client_fd);
    return NULL;
}

int main() {
    int server_fd, client_fd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_addr_len = sizeof(client_addr);
    pthread_t thread_id;

    // Create server socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    // Setup server address structure
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY; // Listen on all interfaces
    server_addr.sin_port = htons(PORT);

    // Bind the socket to the port
    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Listen for incoming connections
    if (listen(server_fd, 5) < 0) {
        perror("Listen failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d...\n", PORT);

    // Accept and handle client connections
    while (1) {
        client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_addr_len);
        if (client_fd < 0) {
            perror("Accept failed");
            continue;
        }

        printf("Client connected from IP: %s, Port: %d. Handling client...\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        // Create a new thread to handle this client
        if (pthread_create(&thread_id, NULL, handle_client, (void *)&client_fd) != 0) {
            perror("Thread creation failed");
            continue;
        }

        // Detach the thread so it can clean up resources when finished
        pthread_detach(thread_id);
    }

    close(server_fd);
    return 0;
}
