# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -Wextra -std=c++17

# Target executable
TARGET = main

# Source files
SRCS = main.cpp

# Benchmark report filenames
REPORTS = benchmark_10c_10k.txt benchmark_10c_100k.txt benchmark_10c_1000k.txt \
          benchmark_100c_10k.txt benchmark_100c_100k.txt benchmark_100c_1000k.txt \
          benchmark_1000c_10k.txt benchmark_1000c_100k.txt benchmark_1000c_1000k.txt

# Default rule
all: $(TARGET)

# Compile the main program
$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRCS)

# Run BlinkDB server in the background and execute all benchmark tests
benchmark: $(TARGET)
	@echo "Starting BlinkDB server..."
	@./$(TARGET) & sleep 2 && \
	( \
		echo "Running benchmark with 10 clients, 10k requests..."; \
		redis-benchmark -p 9001 -t set,get -c 10 -n 10000 > benchmark_10c_10k.txt; \
		echo "Running benchmark with 10 clients, 100k requests..."; \
		redis-benchmark -p 9001 -t set,get -c 10 -n 100000 > benchmark_10c_100k.txt; \
		echo "Running benchmark with 10 clients, 1M requests..."; \
		redis-benchmark -p 9001 -t set,get -c 10 -n 1000000 > benchmark_10c_1000k.txt; \
		echo "Running benchmark with 100 clients, 10k requests..."; \
		redis-benchmark -p 9001 -t set,get -c 100 -n 10000 > benchmark_100c_10k.txt; \
		echo "Running benchmark with 100 clients, 100k requests..."; \
		redis-benchmark -p 9001 -t set,get -c 100 -n 100000 > benchmark_100c_100k.txt; \
		echo "Running benchmark with 100 clients, 1M requests..."; \
		redis-benchmark -p 9001 -t set,get -c 100 -n 1000000 > benchmark_100c_1000k.txt; \
		echo "Running benchmark with 1000 clients, 10k requests..."; \
		redis-benchmark -p 9001 -t set,get -c 1000 -n 10000 > benchmark_1000c_10k.txt; \
		echo "Running benchmark with 1000 clients, 100k requests..."; \
		redis-benchmark -p 9001 -t set,get -c 1000 -n 100000 > benchmark_1000c_100k.txt; \
		echo "Running benchmark with 1000 clients, 1M requests..."; \
		redis-benchmark -p 9001 -t set,get -c 1000 -n 1000000 > benchmark_1000c_1000k.txt; \
	)

# Clean build files and benchmark reports
clean:
	rm -f $(TARGET) $(REPORTS)

