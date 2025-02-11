#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int main() {
    int sock;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];

    // Create socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    // Setup server address structure
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1"); // Connect to localhost (can change to server IP)

    // Connect to the server
    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Connection failed");
        close(sock);
        exit(EXIT_FAILURE);
    }

    printf("Connected to the server.\n");

    // Communication loop
    while (1) {
        printf("Enter message: ");
        fgets(buffer, BUFFER_SIZE, stdin);

        // Remove newline character from input
        buffer[strcspn(buffer, "\n")] = 0;

        // Send message to server
        send(sock, buffer, strlen(buffer), 0);

        // If the user types "exit", break out of the loop
        if (strncmp(buffer, "exit", 4) == 0) {
            printf("Exiting client.\n");
            break;
        }

        // Receive acknowledgment from the server
        memset(buffer, 0, BUFFER_SIZE);
        int bytes_received = recv(sock, buffer, sizeof(buffer) - 1, 0);
        if (bytes_received > 0) {
            printf("Server: %s\n", buffer);
        } else if (bytes_received == 0) {
            printf("Server disconnected\n");
            break;
        } else {
            perror("Receive failed");
            break;
        }
    }

    // Close the socket
    close(sock);

    return 0;
}
