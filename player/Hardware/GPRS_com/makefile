UNAME := $(shell uname)
$(warning $(UNAME))
UNAME_P := $(shell gcc -dumpmachine)
$(warning $(UNAME_P))
CC=gcc
CFLAGS= -Wall
LDFLAGS=-lwiringPi
EXEC=hardware

ifneq (,$(filter armv7%,$(UNAME_P)))
$(warning rpiB2 -> build hardware7)
EXEC=gsm7
else
$(warning rpiA+/B+ -> build hardware6)
EXEC=gsm6
endif

SRC= $(wildcard *.c)
OBJ= $(SRC:.c=.o)
H= $(SRC:.c=.h)

all: $(EXEC)

ifneq (,$(filter armv7%,$(UNAME_P)))
hardware7: $(OBJ)
	$(CC) -o $@ $^ $(LDFLAGS)
else
hardware6: $(OBJ)
	$(CC) -o $@ $^ $(LDFLAGS)
endif

main.o: $(H)

%.o: %.c
	$(CC) -o $@ -c $< $(CFLAGS)

.PHONY: clean mrproper

clean:
	rm -rf *.o
	rm -f $(EXEC)

mrproper: clean
	rm -rf $(EXEC)
