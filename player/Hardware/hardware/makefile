UNAME := $(shell uname)
UNAME_P := $(shell gcc -dumpmachine)
CC=g++
CFLAGS=
LDFLAGS=-lwiringPi

ifeq (,$(findstring arm7,$(UNAME_P)))
  $(warning rpiB2 -> build hardware7)
  EXEC=hardware7
else
  $(warning rpiA+/B+ -> build hardware6)
  EXEC=hardware6
endif

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
clean:
  rm -rf $(EXEC)

mrproper: clean
	rm -rf $(EXEC)
