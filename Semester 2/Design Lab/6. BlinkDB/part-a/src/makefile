# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -Wextra -std=c++17

# Target executable
TARGET = main

# Source files
SRCS = main.cpp

# Object files
OBJS = $(SRCS:.cpp=.o)

# Phony targets (not actual files)
.PHONY: all build run doc clean

# "all" will compile, then generate docs, then run the program
all: build doc run

# Compile the main program
build: $(TARGET)

$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRCS)

# Generate documentation using Doxygen and rename the PDF
doc:
	@echo "Generating documentation..."
	doxygen Doxyfile
	$(MAKE) -C ../docs/latex
	mv ../docs/latex/refman.pdf ../docs/latex/report.pdf
	@echo "Documentation generated at docs/html and docs/latex/report.pdf"

# Run the BlinkDB program
run:
	@echo "Running BlinkDB..."
	./$(TARGET)

# Clean build files
clean:
	rm -f $(TARGET) $(OBJS)
