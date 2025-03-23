# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -Wextra -std=c++17

# Target executable
TARGET = main

# Source files (assuming main.cpp is in the current directory; adjust path if necessary)
SRCS = main.cpp

# Benchmark report filenames (stored in the result folder)
REPORTS = ../result/result_10000_10.txt ../result/result_100000_10.txt ../result/result_1000000_10.txt \
          ../result/result_10000_100.txt ../result/result_100000_100.txt ../result/result_1000000_100.txt \
          ../result/result_10000_1000.txt ../result/result_100000_1000.txt ../result/result_1000000_1000.txt

# Phony targets
.PHONY: all doc build run benchmark clean

# 'all' does: doc -> build -> run
all: doc run

###############################################################################
# 1. Generate Doxygen documentation (HTML + PDF) FIRST
###############################################################################
doc:
	@echo "Generating Doxygen documentation..."
	doxygen Doxyfile
	@if [ -d ../docs/latex ]; then \
	  $(MAKE) -C ../docs/latex; \
	  mv ../docs/latex/refman.pdf ../docs/latex/report.pdf 2>/dev/null || true; \
	  echo "PDF documentation available at docs/latex/report.pdf"; \
	else \
	  echo "docs/latex not found. Check your Doxyfile for GENERATE_LATEX=YES."; \
	fi
	@echo "HTML documentation available in docs/html/index.html"

###############################################################################
# 2. Build the main program
###############################################################################
build: $(TARGET)

$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRCS)

###############################################################################
# 3. Run the BlinkDB server
###############################################################################
run: build
	@echo "Running BlinkDB server..."
	./$(TARGET)

###############################################################################
# Benchmark: Runs the server in the background and executes redis-benchmark
###############################################################################
benchmark: $(TARGET)
	@echo "Starting BlinkDB server..."
	# Create the result folder if it does not exist
	@mkdir -p ../result
	@./$(TARGET) & sleep 2 && \
	( \
		echo "Running benchmark with 10 clients, 10k requests..."; \
		redis-benchmark -p 9001 -t set,get -c 10 -n 10000 > ../result/result_10000_10.txt; \
		echo "Running benchmark with 10 clients, 100k requests..."; \
		redis-benchmark -p 9001 -t set,get -c 10 -n 100000 > ../result/result_100000_10.txt; \
		echo "Running benchmark with 10 clients, 1M requests..."; \
		redis-benchmark -p 9001 -t set,get -c 10 -n 1000000 > ../result/result_1000000_10.txt; \
		echo "Running benchmark with 100 clients, 10k requests..."; \
		redis-benchmark -p 9001 -t set,get -c 100 -n 10000 > ../result/result_10000_100.txt; \
		echo "Running benchmark with 100 clients, 100k requests..."; \
		redis-benchmark -p 9001 -t set,get -c 100 -n 100000 > ../result/result_100000_100.txt; \
		echo "Running benchmark with 100 clients, 1M requests..."; \
		redis-benchmark -p 9001 -t set,get -c 100 -n 1000000 > ../result/result_1000000_100.txt; \
		echo "Running benchmark with 1000 clients, 10k requests..."; \
		redis-benchmark -p 9001 -t set,get -c 1000 -n 10000 > ../result/result_10000_1000.txt; \
		echo "Running benchmark with 1000 clients, 100k requests..."; \
		redis-benchmark -p 9001 -t set,get -c 1000 -n 100000 > ../result/result_100000_1000.txt; \
		echo "Running benchmark with 1000 clients, 1M requests..."; \
		redis-benchmark -p 9001 -t set,get -c 1000 -n 1000000 > ../result/result_1000000_1000.txt; \
	)

###############################################################################
# Clean build files and benchmark reports
###############################################################################
clean:
	rm -f $(TARGET)
	rm -f $(REPORTS)
