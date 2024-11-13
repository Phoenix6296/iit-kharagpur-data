CXX = g++


CXXFLAGS = -std=c++20 -pthread -O2


TARGET = 24CS60R71_A9_part3


SRCS = 24CS60R71_A9_part3.cpp


OBJS = $(SRCS:.cpp=.o)


all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@


clean:
	rm -f $(OBJS) $(TARGET)

run: $(TARGET)
	./$(TARGET)


report: $(TARGET)
	./$(TARGET) && cat 24CS60R71_A9_part3_report.txt