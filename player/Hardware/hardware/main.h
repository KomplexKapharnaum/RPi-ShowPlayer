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

void beforekill(int signum);
void myInterruptCARTE (void);
void myInterruptTELECO(void);
void killthread();
int parseInput(std::string input);
void testRoutine(int n);
void sendStatusTeleco();