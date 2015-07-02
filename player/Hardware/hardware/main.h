//
//  main.h
//  testc
//
//  Created by SuperPierre on 10/12/2014.
//
//

#ifndef __testc__main__
#define __testc__main__

#include <iostream>

#endif /* defined(__testc__main__) */

using namespace std; //for native use of string

bool live=true;

//string to hold data from pyton program
string carte_name;
string carte_ip;
string scene="-";
string version_py="-";
string version_c="1.1";
string status="-";
string voltage="-";
int manualLightMode=1;
string buttonline="OK   B   A";
string popup[11][2];
int init=0;
bool timertitreur=false;

//safe queue to put message in
Queue<string> q;
Timer t;


//C object of hardware
Carte mycarte;
Teleco myteleco;
Titreur mytitreur;

void beforekill(int signum);
void myInterruptCARTE (void);
void myInterruptTELECO(void);
void killthread();
int parseInput(std::string input);
void testRoutine(int n);
void sendStatusTeleco();
void produce(Queue<string>& q, string message);
void readcin(Queue<string>& q);
void consume(Queue<string>& q);
