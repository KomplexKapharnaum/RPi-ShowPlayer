//
//  teleco.h
//  testc
//
//  Created by SuperPierre on 24/03/2015.
//
//

#ifndef __testc__teleco__
#define __testc__teleco__

#include <iostream>
#include "carte.h"


//VALUE FOR PINOUT
#define T_LEDRVALUE 0
#define T_LEDVVALUE 1
#define T_LEDOKVALUE 2
#define T_INTERRUPT 3
//VALUE FOR PININ
#define T_PUSHA 4
#define T_PUSHB 5
#define T_PUSHROTARY 6
#define T_PUSHOK 7
#define T_REED 8
//VALUE FOR PININ ANALOG
#define T_FLOAT 9
//meta
#define T_COUNTVAL 10
#define T_TELECOMODE 11
#define T_BOARDCHECKFLOAT 12
//ledstrob
#define T_STROBLRSPEED 13
#define T_STROBLVSPEED 14
#define T_STROBLOKSPEED 15

#define T_STRING 16
#define T_INIT 17

//size of table
#define T_REGISTERSIZE 18

#define READCOMMAND 0x40
#define WRITECOMMANDVALUE 0xc0
#define WRITECOMMANDFADE 0x80
#define COMMANDMASK 0xC0

#define T_DECINPIN 4
#define T_DECALALOGPIN 9

#define T_MODEBASE 1

#define T_INPUT 1
#define T_OUTPUT 1

#define T_START 99;



class Teleco : public Carte {
  int uninit;

public:
  void initCarte();
  void sendString(char Str1[], char Str2[],char Str3[], char Str4[]);
  int fisrtView();
  void start();
  int readInterrupt();
};


#endif /* defined(__testc__teleco__) */
