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
#include <string>


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
#define T_DISPLAY_LOCK 10
#define T_TELECOMODE 11
#define T_BOARDCHECKFLOAT 12
//ledstrob
#define T_STROBLRSPEED 13
#define T_STROBLVSPEED 14
#define T_STROBLOKSPEED 15

#define T_INIT 16
#define T_LOCK 17

#define T_STRING 18
#define T_POPUP 19
#define T_BUTON_STRING 20


//size of table
#define T_REGISTERSIZE 21

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

#define T_ISOPEN 0
#define T_ISLOCK 1
#define T_ISLOCKWITHSLEEP 2
#define T_POWEROFF 10

#define T_MENU_ID_SHOW_STATUS 1
#define T_MENU_ID_STATUS_AUTO_NAME_IP_VOLTAGE 2
#define T_MENU_ID_STATUS_GIT_VERSION 3
#define T_MENU_ID_STATUS_SCENE 4
#define T_MENU_ID_STATUS_USB 5
#define T_MENU_ID_STATUS_MEDIA 6
#define T_MENU_ID_STATUS_SYNC 7
#define T_MENU_ID_STATUS_USER 8
#define T_MENU_ID_STATUS_ERROR 9

#define T_MENU_ID_LOG_0 10




class Teleco : public Carte {
  int uninit;
  char localpoweroff;

private:
  char lockCom;

public:
  void initCarte(char pow);
  bool sendString(char Str1[], char Str2[],int val);
  void sendButtonString(char Str1[]);
  int fisrtView();
  void start();
  void reset();
  int readInterrupt();
  void setLedOk(int val);
  void setLedWarning(int val);
  int readOrSetTelecoLock(int val=-1);
  int needtestroutine;
  int needstart;
};


#endif /* defined(__testc__teleco__) */
