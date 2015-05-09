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

#define TELECO_MESSAGE_PREVIOUSSCENE 1
#define TELECO_MESSAGE_PREVIOUSSCENE_GROUP 2
#define TELECO_MESSAGE_PREVIOUSSCENE_ALL_SYNC 3
#define TELECO_MESSAGE_RESTARTSCENE 4
#define TELECO_MESSAGE_RESTARTSCENE_GROUP 5
#define TELECO_MESSAGE_RESTARTSCENE_ALL_SYNC 6
#define TELECO_MESSAGE_NEXTSCENE 7
#define TELECO_MESSAGE_NEXTSCENE_GROUP 8
#define TELECO_MESSAGE_NEXTSCENE_ALL_SYNC 9

#define TELECO_MESSAGE_SETTINGS_LOG_DEBUG 20
#define TELECO_MESSAGE_SETTINGS_LOG_ERROR 21
#define TELECO_MESSAGE_SETTINGS_VOLPLUS 22
#define TELECO_MESSAGE_SETTINGS_VOLMOINS 23
#define TELECO_MESSAGE_SETTINGS_VOLSAVE 24
#define TELECO_MESSAGE_SETTINGS_VOLBACK 25

#define TELECO_MESSAGE_MODE_SHOW 30
#define TELECO_MESSAGE_MODE_REPET 31
#define TELECO_MESSAGE_MODE_DEBUG 32
#define TELECO_MESSAGE_LOG_ERROR 33
#define TELECO_MESSAGE_LOG_DEBUG 34

#define TELECO_MESSAGE_BLINKGROUP 40
#define TELECO_MESSAGE_TESTROUTINE 41

#define TELECO_MESSAGE_SYS_RESTARTPY 50
#define TELECO_MESSAGE_SYS_RESTARTWIFI 51
#define TELECO_MESSAGE_SYS_UPDATESYS 52
#define TELECO_MESSAGE_SYS_POWEROFF 53
#define TELECO_MESSAGE_SYS_REBOOT 54

#define TELECO_MESSAGE_GET_INFO 60

#define TELECO_MESSAGE_MEDIA_VOLPLUS 70
#define TELECO_MESSAGE_MEDIA_VOLPLUS_GROUP 71
#define TELECO_MESSAGE_MEDIA_VOLPLUS_ALL_SYNC 72
#define TELECO_MESSAGE_MEDIA_VOLMOINS 73
#define TELECO_MESSAGE_MEDIA_VOLMOINS_GROUP 74
#define TELECO_MESSAGE_MEDIA_VOLMOINS_ALL_SYNC 75
#define TELECO_MESSAGE_MEDIA_MUTE 76
#define TELECO_MESSAGE_MEDIA_MUTE_GROUP 77
#define TELECO_MESSAGE_MEDIA_MUTE_ALL_SYNC 78
#define TELECO_MESSAGE_MEDIA_PAUSE 79
#define TELECO_MESSAGE_MEDIA_PAUSE_GROUP 80
#define TELECO_MESSAGE_MEDIA_PLAY 81
#define TELECO_MESSAGE_MEDIA_PLAY_GROUP 82
#define TELECO_MESSAGE_MEDIA_STOP 83
#define TELECO_MESSAGE_MEDIA_STOP_GROUP 84




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
