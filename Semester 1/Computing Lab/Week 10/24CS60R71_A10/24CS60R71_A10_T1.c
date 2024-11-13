#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <signal.h>
#include <unistd.h>
#include <stdbool.h>

void handle_signal(int sig)
{
    printf("\nI am unstoppable!\n> ");
    fflush(stdout);
}

int main()
{
    char input;
    signal(SIGINT, handle_signal);
    while (true)
    {
        printf("> ");
        input = getchar();
        if (input == '\n')
            continue;
        if (input == 'x')
        {
            printf("Valar Morghulis\n");
            break;
        }
        if (isalpha(input) && input != 'x')
            printf("%c\n", input);
        else if (!isalpha(input) && input != '\n')
            printf("Do you speak my language?\n");

        while (getchar() != '\n')
            ;
    }
    return 0;
}
