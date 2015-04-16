UNAME := $(shell uname)
UNAME_P := $(shell gcc -dumpmachine)
CC=g++
CFLAGS=
LDFLAGS=-lwiringPi
EXEC=hardware
SRC= $(wildcard *.cpp)
OBJ= $(SRC:.cpp=.o)
H= $(SRC:.cpp=.h)

all: $(EXEC)

hardware: $(OBJ)
	$(CC) -o $@ $^ $(LDFLAGS)

main.o: $(H)

%.o: %.cpp
	$(CC) -o $@ -c $< $(CFLAGS)

.PHONY: clean mrproper

clean:
	rm -rf *.o

mrproper: clean
	rm -rf $(EXEC)
all:
  $(warning arch -$(OS) -$(PROCESSOR_ARCHITECTURE) -$(UNAME_S) -$(UNAME_P) -$(UNAME))