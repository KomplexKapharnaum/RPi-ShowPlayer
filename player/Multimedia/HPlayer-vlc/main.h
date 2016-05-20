#include <string>
using std::string;

#include <stdio.h>
#include <iostream>
using std::getline;
using std::cout;
using std::cin;

#include <stdlib.h>
#include <unistd.h>

#include <signal.h>
#include "dualPlayer.h"
#include <algorithm>
#include <pthread.h>
#include "Queue.h"

Queue* inputQueue;
pthread_t consumer;
dualPlayer *player;
bool running;