#include <iostream>
#include <thread>
#include <vector>
#include <cstdlib>
#include <chrono>
#include <stdexcept>
#include <atomic>
#include <coroutine>
#include <functional>
#include <optional>
#include <fstream>
#include <queue>
#include <mutex>

using namespace std;

// Constants
const int MAX_OPERATIONS = 100;    // Number of operations to execute
const int THREAD_POOL_SIZE = 5;    // Size of the thread pool
std::atomic<bool> isRunning(true); // Flag for thread pool running state

// Lock-free job queue
template <typename T>
class LockFreeQueue
{
public:
    void enqueue(T task)
    {
        std::lock_guard<std::mutex> lock(queueMutex);
        taskQueue.push(task);
    }

    std::optional<T> dequeue()
    {
        std::lock_guard<std::mutex> lock(queueMutex);
        if (taskQueue.empty())
            return std::nullopt;

        T task = taskQueue.front();
        taskQueue.pop();
        return task;
    }

private:
    std::queue<T> taskQueue;
    std::mutex queueMutex;
};

// Coroutine result structure
template <typename T>
struct CoroutineResult
{
    struct promise_type
    {
        T value;

        CoroutineResult get_return_object()
        {
            return CoroutineResult{std::coroutine_handle<promise_type>::from_promise(*this)};
        }

        auto initial_suspend() { return std::suspend_always{}; }
        auto final_suspend() noexcept { return std::suspend_always{}; }
        void unhandled_exception() { std::terminate(); }

        void return_value(T v) { value = v; }
    };

    std::coroutine_handle<promise_type> handle;

    T get()
    {
        return handle.promise().value;
    }

    void resume()
    {
        if (!handle.done())
            handle.resume();
    }

    bool is_ready() const
    {
        return handle.done(); // Check if the coroutine has completed
    }
};

// Asynchronous mathematical functions
CoroutineResult<int> async_add(int a, int b) { co_return a + b; }
CoroutineResult<int> async_subtract(int a, int b) { co_return a - b; }
CoroutineResult<int> async_multiply(int a, int b) { co_return a *b; }
CoroutineResult<int> async_divide(int a, int b)
{
    if (b == 0)
    {
        co_return std::numeric_limits<int>::max(); // Return a special value indicating division by zero
    }
    co_return a / b;
}

// Task System to manage and schedule coroutines
class CoroutineTaskSystem
{
public:
    void addTask(std::function<CoroutineResult<int>()> task)
    {
        std::lock_guard<std::mutex> lock(taskMutex);
        tasks.push(task);
    }

    void pollAndRun()
    {
        std::lock_guard<std::mutex> lock(taskMutex);
        while (!tasks.empty())
        {
            auto task = tasks.front();
            tasks.pop();
            auto result = task(); // Run the coroutine
            if (!result.is_ready())
            {
                pendingTasks.push(result); // Re-add to pending if not ready
            }
            else
            {
                std::cout << "Result: " << result.get() << std::endl;
            }
        }
    }

    void processPendingTasks()
    {
        std::lock_guard<std::mutex> lock(taskMutex);
        queue<CoroutineResult<int>> tempQueue;
        while (!pendingTasks.empty())
        {
            auto result = pendingTasks.front();
            pendingTasks.pop();
            if (!result.is_ready())
                tempQueue.push(result); // Still not ready, keep it in pending
            else
            {
                result.resume(); // Resume the coroutine if ready
                int value = result.get();
                if (value == std::numeric_limits<int>::max())
                {
                    std::cout << "Pending Result: Division by zero error" << std::endl;
                }
                else
                {
                    std::cout << "Pending Result: " << value << std::endl;
                }
            }
        }
        std::swap(pendingTasks, tempQueue); // Re-add pending tasks
    }

private:
    std::queue<std::function<CoroutineResult<int>()>> tasks; // Scheduled tasks
    std::queue<CoroutineResult<int>> pendingTasks;           // Pending coroutine results
    std::mutex taskMutex;
};

// Forward declaration of ThreadPool
class ThreadPool;

// Job Assigner to efficiently assign jobs to the thread pool
class JobAssigner
{
public:
    JobAssigner(ThreadPool &pool) : threadPool(pool) {}

    void submitJob(int a, int b, int operation);

private:
    ThreadPool &threadPool; // Reference to the thread pool
};

// Thread Pool class with CoroutineTaskSystem
class ThreadPool
{
public:
    ThreadPool()
    {
        threads.reserve(THREAD_POOL_SIZE);
        for (int i = 0; i < THREAD_POOL_SIZE; ++i)
        {
            threads.emplace_back(&ThreadPool::workerThread, this);
        }
    }

    ~ThreadPool()
    {
        isRunning = false;
        for (auto it = threads.begin(); it != threads.end(); ++it)
            if (it->joinable())
                it->join();
    }

    template <typename F>
    void enqueue(F task)
    {
        taskQueue.enqueue(task);
    }

    void workerThread()
    {
        CoroutineTaskSystem taskSystem;

        for (; isRunning;)
        {
            auto task = taskQueue.dequeue();
            if (task)
                taskSystem.addTask(*task); // Add task to the system

            taskSystem.pollAndRun();          // Poll and run ready coroutines
            taskSystem.processPendingTasks(); // Check for pending tasks

            std::this_thread::sleep_for(std::chrono::milliseconds(1)); // Prevent busy waiting
        }
    }

private:
    std::vector<std::thread> threads;
    LockFreeQueue<std::function<CoroutineResult<int>()>> taskQueue;
};

// Implementation of JobAssigner submitJob method
void JobAssigner::submitJob(int a, int b, int operation)
{
    if (operation == 0)
    {
        threadPool.enqueue([=]() -> CoroutineResult<int>
                           {
            auto result = async_add(a, b);
            co_return result.get(); });
    }
    else if (operation == 1)
    {
        threadPool.enqueue([=]() -> CoroutineResult<int>
                           {
            auto result = async_subtract(a, b);
            co_return result.get(); });
    }
    else if (operation == 2)
    {
        threadPool.enqueue([=]() -> CoroutineResult<int>
                           {
            auto result = async_multiply(a, b);
            co_return result.get(); });
    }
    else if (operation == 3)
    {
        threadPool.enqueue([=]() -> CoroutineResult<int>
                           {
            auto result = async_divide(a, b);
            co_return result.get(); });
    }
}

// Traditional blocking version for performance comparison
int add(int a, int b) { return a + b; }
int subtract(int a, int b) { return a - b; }
int multiply(int a, int b) { return a * b; }
int divide(int a, int b)
{
    if (b == 0)
    {
        throw std::runtime_error("Division by zero");
    }
    return a / b;
}

// Performance comparison function
void testBlockingSystem()
{
    std::cout << "Starting blocking execution:\n";
    for (int i = 0; i < MAX_OPERATIONS; ++i)
    {
        int a = std::rand() % 100;
        int b = std::rand() % 100;

        int operation = std::rand() % 4;
        switch (operation)
        {
        case 0:
            std::cout << "Task " << i << ": " << add(a, b) << std::endl;
            break;
        case 1:
            std::cout << "Task " << i << ": " << subtract(a, b) << std::endl;
            break;
        case 2:
            std::cout << "Task " << i << ": " << multiply(a, b) << std::endl;
            break;
        case 3:
            try
            {
                std::cout << "Task " << i << ": " << divide(a, b) << std::endl;
            }
            catch (const std::runtime_error &e)
            {
                std::cout << "Task " << i << ": Division by zero error" << std::endl;
            }
            break;
        }
    }
}

// Non-blocking coroutine-based system
void testNonBlockingSystem(ThreadPool &pool)
{
    std::cout << "Starting non-blocking execution:\n";
    JobAssigner assigner(pool);

    for (int i = 0; i < MAX_OPERATIONS; ++i)
    {
        int a = std::rand() % 100;
        int b = std::rand() % 100;

        int operation = std::rand() % 4;
        assigner.submitJob(a, b, operation);
    }
}

int main()
{
    std::srand(static_cast<unsigned int>(std::time(0))); // Initialize random seed

    // Measure performance of traditional blocking version
    auto startBlocking = std::chrono::high_resolution_clock::now();
    testBlockingSystem();
    auto endBlocking = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> blockingDuration = endBlocking - startBlocking;
    std::cout << "Blocking execution time: " << blockingDuration.count() << " seconds\n";

    // Measure performance of coroutine-based non-blocking version
    ThreadPool pool; // Create thread pool
    auto startNonBlocking = std::chrono::high_resolution_clock::now();
    testNonBlockingSystem(pool);
    auto endNonBlocking = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> nonBlockingDuration = endNonBlocking - startNonBlocking;
    std::cout << "Non-blocking execution time: " << nonBlockingDuration.count() << " seconds\n";

    return 0;
}
