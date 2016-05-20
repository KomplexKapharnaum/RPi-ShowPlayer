UNAME := $(shell uname)
$(warning $(UNAME))
UNAME_P := $(shell gcc -dumpmachine)
$(warning $(UNAME_P))
CC=g++
CFLAGS=-std=c++11 -Wall
LDFLAGS=-lwiringPi -llo
EXEC=hardware

ifneq (,$(filter armv7%,$(UNAME_P)))
$(warning rpiB2 -> build gsm7)
EXEC=gsm7
else
$(warning rpiA+/B+ -> build gsm6)
EXEC=gsm6
endif

SRC= $(wildcard *.cpp)
OBJ= $(SRC:.cpp=.o)
H= $(SRC:.cpp=.h)

all: $(EXEC)

ifneq (,$(filter armv7%,$(UNAME_P)))
gsm7: $(OBJ)
	$(CC) -o $@ $^ $(LDFLAGS)
else
gsm6: $(OBJ)
	$(CC) -o $@ $^ $(LDFLAGS)
endif

main.o: $(H)

%.o: %.cpp
	$(CC) -o $@ -c $< $(CFLAGS)

.PHONY: clean mrproper

clean:
	rm -rf *.o
	rm -f $(EXEC)

mrproper: clean
	rm -rf $(EXEC)
