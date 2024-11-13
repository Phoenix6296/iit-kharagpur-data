CXX = g++
CXXFLAGS = -std=c++20 -pthread -O2
TARGET = 24CS60R71_A9_part2


all: $(TARGET)

$(TARGET): 24CS60R71_A9_part2.cpp
	$(CXX) $(CXXFLAGS) -o $(TARGET) 24CS60R71_A9_part2.cpp


run: $(TARGET)
	./$(TARGET)


clean:
	rm -f $(TARGET) *.txt


.PHONY: all run clean