#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <semaphore.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/wait.h>
#include <fcntl.h>

#define UNPROCESSED -1
#define PROCESSED 1
#define MATRIX_SIZE 1000

typedef struct
{
    int m, n;
    int (*matrix)[MATRIX_SIZE];
    int *a;
    int *b;
    pthread_mutex_t matrixMutex;
    sem_t *chaosSem;
    sem_t *orderSem;
} SharedData;

void createRandomMatrix(SharedData *data)
{
    for (int i = 0; i < data->m; i++)
        for (int j = 0; j < data->n; j++)
            data->matrix[i][j] = rand() % 1000 + 1;
    printf("Random Matrix M of size (%d,%d) created in shared memory.\n", data->m, data->n);
}

void chaosProcess(SharedData *data)
{
    for (int k = 0; k < 30; k++)
    {
        int i = rand() % data->m;
        int j = rand() % data->n;
        int value = rand() % 1000 + 1;

        sem_wait(data->chaosSem);
        pthread_mutex_lock(&data->matrixMutex);

        data->matrix[i][j] = value;
        data->a[i] = PROCESSED;
        data->b[i] = UNPROCESSED;
        printf("Chaos: Updated element at cell %d x %d with value %d.\n", i, j, value);

        pthread_mutex_unlock(&data->matrixMutex);
        sem_post(data->chaosSem);

        sleep(2);
    }
    printf("CHAOS PROCESS ENDS\n");
}

void orderProcess(SharedData *data)
{
    for (int k = 0; k < 30; k++)
    {
        sem_wait(data->orderSem);

        for (int i = 0; i < data->m; i++)
        {
            if (data->a[i] == PROCESSED && data->b[i] == UNPROCESSED)
            {
                pthread_mutex_lock(&data->matrixMutex);

                printf("Order: Detected updated element at row %d.\n", i);
                printf("Order: row %d is sorted now.\n", i);
                printf("Order: older row %d: ", i);
                for (int j = 0; j < data->n; j++)
                    printf("%d ", data->matrix[i][j]);
                printf("\n");

                for (int a = 0; a < data->n - 1; a++)
                {
                    for (int b = a + 1; b < data->n; b++)
                    {
                        if (data->matrix[i][a] > data->matrix[i][b])
                        {
                            int temp = data->matrix[i][a];
                            data->matrix[i][a] = data->matrix[i][b];
                            data->matrix[i][b] = temp;
                        }
                    }
                }
                data->b[i] = PROCESSED;

                printf("Order: new row %d: ", i);
                for (int j = 0; j < data->n; j++)
                    printf("%d ", data->matrix[i][j]);
                printf("\n");

                pthread_mutex_unlock(&data->matrixMutex);
                break;
            }
        }
        sem_post(data->orderSem);
        // usleep(500000);
    }
    printf("ORDER PROCESS ENDS\n");
}

void printMatrix(SharedData *data)
{
    printf("Final matrix:\n");
    for (int i = 0; i < data->m; i++)
    {
        for (int j = 0; j < data->n; j++)
            printf("%d ", data->matrix[i][j]);
        printf("\n");
    }
}

int main()
{
    pid_t pid;
    SharedData data;

    printf("Enter the number of rows and columns (m): ");
    scanf("%d %d", &data.m, &data.n);

    int shmId = shmget(IPC_PRIVATE, sizeof(int) * data.m * data.n + 2 * MATRIX_SIZE * sizeof(int), IPC_CREAT | 0666);
    if (shmId < 0)
    {
        perror("shmget failed");
        exit(1);
    }

    int *sharedMemory = shmat(shmId, NULL, 0);
    if (sharedMemory == (void *)-1)
    {
        perror("shmat failed");
        exit(1);
    }

    data.matrix = (int(*)[MATRIX_SIZE])sharedMemory;
    data.a = sharedMemory + data.m * data.n;
    data.b = data.a + MATRIX_SIZE;

    for (int i = 0; i < MATRIX_SIZE; i++)
        data.a[i] = data.b[i] = UNPROCESSED;

    createRandomMatrix(&data);
    printMatrix(&data);

    data.chaosSem = sem_open("/chaosSem", O_CREAT, 0644, 2);
    if (data.chaosSem == SEM_FAILED)
    {
        perror("sem_open for chaosSem failed");
        exit(1);
    }

    data.orderSem = sem_open("/orderSem", O_CREAT, 0644, 5);
    if (data.orderSem == SEM_FAILED)
    {
        perror("sem_open for orderSem failed");
        exit(1);
    }

    pthread_mutex_init(&data.matrixMutex, NULL);

    for (int i = 0; i < 3; i++)
    {
        pid = fork();
        if (pid == 0)
        {
            printf("I am chaos process %d\n", i + 1);
            chaosProcess(&data);
            exit(0);
        }
        else if (pid < 0)
        {
            perror("fork failed for chaos process");
            exit(1);
        }
    }

    for (int i = 0; i < 6; i++)
    {
        pid = fork();
        if (pid == 0)
        {
            printf("I am order process %d\n", i + 1);
            orderProcess(&data);
            exit(0);
        }
        else if (pid < 0)
        {
            perror("fork failed for order process");
            exit(1);
        }
    }

    for (int i = 0; i < 9; i++)
        wait(NULL);

    printMatrix(&data);

    shmdt(sharedMemory);
    shmctl(shmId, IPC_RMID, NULL);

    pthread_mutex_destroy(&data.matrixMutex);
    sem_close(data.chaosSem);
    sem_close(data.orderSem);
    sem_unlink("/chaosSem");
    sem_unlink("/orderSem");

    return 0;
}
