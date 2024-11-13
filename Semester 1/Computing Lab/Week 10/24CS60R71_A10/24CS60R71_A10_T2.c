#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <time.h>

#define MAX_SIZE 1000
#define UNPROCESSED -1
#define PROCESSED 1

typedef struct
{
    int **matrix;
    int *rowIndex;
    int *rowStatus;
    int rows;
    int columns;
    int *chaosUpdates;
    pthread_mutex_t *matrixLock;
    pthread_mutex_t *arrayLock;
    sem_t *semOrder;
} SharedData;

void printMatrix(int **matrix, int rows, int columns)
{
    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < columns; j++)
            printf("%d ", matrix[i][j]);
        printf("\n");
    }
}

// Chaos Thread function
void *chaosThread(void *arg)
{
    SharedData *data = (SharedData *)arg;
    srand(time(NULL));
    for (int i = 0; i < 30; i++)
    {
        int row = rand() % data->rows;
        int col = rand() % data->columns;
        int newValue = rand() % 1000 + 1;

        pthread_mutex_lock(data->matrixLock);
        data->matrix[row][col] = newValue;
        pthread_mutex_unlock(data->matrixLock);

        pthread_mutex_lock(data->arrayLock);
        data->rowIndex[i] = row;
        data->rowStatus[i] = UNPROCESSED;
        (*data->chaosUpdates)++;
        pthread_mutex_unlock(data->arrayLock);

        printf("Chaos: Updated element at cell %d x %d with value %d.\n", row, col, newValue);

        // Signal order threads
        sem_post(data->semOrder);
        sem_post(data->semOrder);
        sem_post(data->semOrder);

        sleep(2);
    }

    printf("CHAOS THREAD ENDS\n");
    pthread_exit(NULL);
}

void insertionSort(int *row, int columns)
{
    for (int i = 1; i < columns; i++)
    {
        int key = row[i];
        int j = i - 1;
        while (j >= 0 && row[j] > key)
        {
            row[j + 1] = row[j];
            j--;
        }
        row[j + 1] = key;
    }
}

void *orderThread(void *arg)
{
    SharedData *data = (SharedData *)arg;
    while (*(data->chaosUpdates) < 30)
    {
        sem_wait(data->semOrder);

        pthread_mutex_lock(data->arrayLock);
        int processed = 0;
        int rowToSort = -1;

        for (int i = 0; i < 30; i++)
        {
            if (data->rowStatus[i] == UNPROCESSED)
            {
                rowToSort = data->rowIndex[i];
                data->rowStatus[i] = PROCESSED;
                processed = 1;
                break;
            }
        }

        pthread_mutex_unlock(data->arrayLock);

        if (processed && rowToSort != -1)
        {
            pthread_mutex_lock(data->matrixLock);
            printf("Order: Detected updated element at row %d\n", rowToSort);

            printf("Old row %d: ", rowToSort);
            for (int j = 0; j < data->columns; j++)
                printf("%d ", data->matrix[rowToSort][j]);
            printf("\n");

            insertionSort(data->matrix[rowToSort], data->columns);

            printf("New row %d: ", rowToSort);
            for (int j = 0; j < data->columns; j++)
                printf("%d ", data->matrix[rowToSort][j]);
            printf("\n");

            pthread_mutex_unlock(data->matrixLock);
        }
    }

    printf("ORDER THREAD ENDS\n");
    pthread_exit(NULL);
}

int main()
{
    int rows, columns;
    printf("Enter matrix dimensions (rows and columns): ");
    scanf("%d %d", &rows, &columns);

    int **matrix = (int **)malloc(rows * sizeof(int *));
    for (int i = 0; i < rows; i++)
    {
        matrix[i] = (int *)malloc(columns * sizeof(int));
        for (int j = 0; j < columns; j++)
            matrix[i][j] = rand() % 1000 + 1;
    }

    int rowIndex[MAX_SIZE];
    int rowStatus[MAX_SIZE];
    int chaosUpdates = 0;
    pthread_mutex_t matrixLock = PTHREAD_MUTEX_INITIALIZER;
    pthread_mutex_t arrayLock = PTHREAD_MUTEX_INITIALIZER;
    sem_t semOrder;

    for (int i = 0; i < MAX_SIZE; i++)
    {
        rowIndex[i] = -1;
        rowStatus[i] = PROCESSED;
    }

    printf("Random Matrix of size [%d, %d] is created:\n", rows, columns);
    printMatrix(matrix, rows, columns);
    printf("Shared Arrays rowIndex and rowStatus are created.\n");

    // Initialize semaphore
    sem_init(&semOrder, 0, 0);

    SharedData data = {matrix, rowIndex, rowStatus, rows, columns, &chaosUpdates, &matrixLock, &arrayLock, &semOrder};

    pthread_t chaos, order1, order2, order3;
    pthread_create(&chaos, NULL, chaosThread, &data);
    printf("I am chaos\n");

    pthread_create(&order1, NULL, orderThread, &data);
    printf("I am order 1\n");

    pthread_create(&order2, NULL, orderThread, &data);
    printf("I am order 2\n");

    pthread_create(&order3, NULL, orderThread, &data);
    printf("I am order 3\n");

    pthread_join(chaos, NULL);
    pthread_join(order1, NULL);
    pthread_join(order2, NULL);
    pthread_join(order3, NULL);

    printf("Final Matrix:\n");
    printMatrix(matrix, rows, columns);

    for (int i = 0; i < rows; i++)
        free(matrix[i]);
    free(matrix);

    // Destroy semaphore
    sem_destroy(&semOrder);

    return 0;
}