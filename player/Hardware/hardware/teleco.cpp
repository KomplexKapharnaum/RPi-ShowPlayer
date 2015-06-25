//
//  teleco.cpp
//  testc
//
//  Created by SuperPierre on 24/03/2015.
//
//

#include "teleco.h"


#include "extSPI.h"

#include <stdio.h>
#include <fcntl.h>
#include <errno.h>

#include <wiringPi.h>
#include <wiringPiSPI.h>
#include <stdlib.h>
#include <string>


//init remote
void Teleco::initCarte(char pow){
  localpoweroff=pow;
  fprintf(stderr, "\n\x1b[32mteleco - add teleco dnc\n\x1b[0m");
  SPIcarte.initSPI();
  SPIcarte.addChipSelect(19,500000);
  needtestroutine=0;
  needstart=0;
  uninit=1;
  lockCom=0;
}

//check if start
int Teleco::fisrtView(){
  return uninit;
}

//start remote
void Teleco::start(){
  fprintf(stderr, "\x1b[32mteleco - teleco start\n\x1b[0m");
  uninit=0;
  writeValue(T_INIT,1);
  setLedWarning(0);
}

//reset remote
void Teleco::reset(){
  if (uninit==0) {
  fprintf(stderr, "teleco - teleco reset\n");
  setLedWarning(1);
  writeValue(T_INIT,0);
  uninit=1;
  }
}

//acces to led status
void Teleco::setLedOk(int val){
  writeValue(T_LEDOKVALUE,val);
}
void Teleco::setLedWarning(int val){
  writeValue(T_LEDRVALUE,(1-val));
}


//send info to the remote
bool Teleco::sendString(char Str1[], char Str2[], int val){
  if (lockCom==0){
  //setLedWarning(1);
  unsigned char buff[38];
  buff[0]= (char)(WRITECOMMANDVALUE+T_STRING);
  buff[1]= (char)val;
  for(int i=0;i<17;i++){
    buff[i+2]= *(Str1+i);
  }
  for(int i=0;i<17;i++){
    buff[i+2+16]= *(Str2+i);
  }
  fprintf(stderr, "teleco - teleco send string type=%u : %s - %s\n",val,Str1,Str2);
  SPIcarte.send(0,buff,38);
  //setLedWarning(0);
    return true;
  } else {
    fprintf(stderr, "teleco - cant send by lock\n");
    return false;
  }
}

/*
// no use
void Teleco::sendButtonString(char Str1[]){
  unsigned char buff[19];
  buff[0]= (char)(WRITECOMMANDVALUE+T_BUTON_STRING);
  for(int i=0;i<16;i++){
    buff[i+1]= *(Str1+i);
  }
  fprintf(stderr, "teleco - teleco send button string : %s\n",buff);
  SPIcarte.send(0,buff,19);
}
*/

//send lock status
int Teleco::readOrSetTelecoLock(int val){
  int state = readValue(T_LOCK);
  if (val!=-1 && state != val){
    writeValue(T_LOCK,val);
    delay(1);
    return readValue(T_LOCK);
  }
  return state;
}



//read intterupt from teleco and out corresponding message
int Teleco::readInterrupt(){
  setLedWarning(1);
  unsigned char buff[2];
  buff[0]= (char)(READCOMMAND+T_INTERRUPT);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  //fprintf(stderr, "teleco - read i %u",buff[1]);
  int address = buff[1];
  buff[0]= (char)(READCOMMAND+address);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  if(address!=T_DISPLAY_LOCK)fprintf(stderr, "teleco - intterupt %u read %u\n",address,buff[1]);
  int valeur = buff[1];
  setLedWarning(0);
  switch (address) {
    case T_DISPLAY_LOCK:
      //fprintf(stderr, "teleco - lock com %u\n",valeur);
      lockCom=valeur;
      break;
    case T_PUSHA:
      std::cout << "#TELECO_PUSH_A "<< valeur << std::endl;
      break;
    case T_PUSHB:
      std::cout << "#TELECO_PUSH_B "<< valeur << std::endl;
      break;
    case T_PUSHROTARY:
      switch (valeur){

        case TELECO_MESSAGE_PREVIOUSSCENE:
          std::cout << "#TELECO_MESSAGE_PREVIOUSSCENE  Self" << std::endl;
          break;
        case TELECO_MESSAGE_PREVIOUSSCENE_GROUP:
          std::cout << "#TELECO_MESSAGE_PREVIOUSSCENE Group" << std::endl;
          break;
        case TELECO_MESSAGE_PREVIOUSSCENE_ALL_SYNC:
          std::cout << "#TELECO_MESSAGE_PREVIOUSSCENE All" << std::endl;
          break;
        case TELECO_MESSAGE_RESTARTSCENE:
          std::cout << "#TELECO_MESSAGE_RESTARTSCENE  Self" << std::endl;
          break;
        case TELECO_MESSAGE_RESTARTSCENE_GROUP :
          std::cout << "#TELECO_MESSAGE_RESTARTSCENE Group" << std::endl;
          break;
        case TELECO_MESSAGE_RESTARTSCENE_ALL_SYNC :
          std::cout << "#TELECO_MESSAGE_RESTARTSCENE All" << std::endl;
          break;
        case TELECO_MESSAGE_NEXTSCENE :
          std::cout << "#TELECO_MESSAGE_NEXTSCENE Self" << std::endl;
          break;
        case TELECO_MESSAGE_NEXTSCENE_GROUP :
          std::cout << "#TELECO_MESSAGE_NEXTSCENE Group" << std::endl;
          break;
        case TELECO_MESSAGE_NEXTSCENE_ALL_SYNC :
          std::cout << "#TELECO_MESSAGE_NEXTSCENE All" << std::endl;
          break;
          
          
        case TELECO_MESSAGE_SETTINGS_LOG_DEBUG :
          std::cout << "#TELECO_MESSAGE_SETTINGS_LOG_DEBUG" << std::endl;
          break;
        case TELECO_MESSAGE_SETTINGS_LOG_ERROR :
          std::cout << "#TELECO_MESSAGE_SETTINGS_LOG_ERROR" << std::endl;
          break;
        case TELECO_MESSAGE_SETTINGS_VOLPLUS :
          std::cout << "#TELECO_MESSAGE_SETTINGS_VOLPLUS" << std::endl;
          break;
        case TELECO_MESSAGE_SETTINGS_VOLMOINS :
          std::cout << "#TELECO_MESSAGE_SETTINGS_VOLMOINS" << std::endl;
          break;
        case TELECO_MESSAGE_SETTINGS_VOLSAVE :
          std::cout << "#TELECO_MESSAGE_SETTINGS_VOLSAVE" << std::endl;
          break;
        case TELECO_MESSAGE_SETTINGS_VOLBACK :
          std::cout << "#TELECO_MESSAGE_SETTINGS_VOLBACK" << std::endl;
          break;
          
          
        case TELECO_MESSAGE_MODE_SHOW :
          std::cout << "#TELECO_MESSAGE_MODE_SHOW" << std::endl;
          break;
        case TELECO_MESSAGE_MODE_REPET :
          std::cout << "#TELECO_MESSAGE_MODE_REPET" << std::endl;
          break;
        case TELECO_MESSAGE_MODE_DEBUG :
          std::cout << "#TELECO_MESSAGE_MODE_DEBUG" << std::endl;
          break;
        case TELECO_MESSAGE_LOG_ERROR :
          std::cout << "#TELECO_MESSAGE_LOG_ERROR" << std::endl;
          break;
        case TELECO_MESSAGE_LOG_DEBUG :
          std::cout << "#TELECO_MESSAGE_LOG_DEBUG" << std::endl;
          break;
          
          
        case TELECO_MESSAGE_BLINKGROUP :
          std::cout << "#TELECO_MESSAGE_BLINKGROUP" << std::endl;
          break;
        case TELECO_MESSAGE_TESTROUTINE :
          std::cout << "#TELECO_MESSAGE_TESTROUTINE" << std::endl;
          needtestroutine=1;
          break;
          
          
        case TELECO_MESSAGE_SYS_RESTARTPY :
          std::cout << "#TELECO_MESSAGE_SYS_RESTARTPY" << std::endl;
          break;
        case TELECO_MESSAGE_SYS_RESTARTWIFI :
          std::cout << "#TELECO_MESSAGE_SYS_RESTARTWIFI" << std::endl;
          break;
        case TELECO_MESSAGE_SYS_UPDATESYS :
          std::cout << "#TELECO_MESSAGE_SYS_UPDATESYS" << std::endl;
          break;
        case TELECO_MESSAGE_SYS_POWEROFF :
          std::cout << "#TELECO_MESSAGE_SYS_POWEROFF" << std::endl;
          delay(10000);
          system ("sudo shutdown -h now");
          break;
        case TELECO_MESSAGE_SYS_REBOOT :
          std::cout << "#TELECO_MESSAGE_SYS_REBOOT" << std::endl;
          delay(10000);
          system ("sudo reboot");
          break;
          
        case TELECO_MESSAGE_GET_INFO :
          std::cout << "#TELECO_MESSAGE_GET_INFO" << std::endl;
          break;
          
        case TELECO_MESSAGE_MEDIA_VOLPLUS :
          std::cout << "#TELECO_MESSAGE_MEDIA_VOLPLUS  Self" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_VOLPLUS_GROUP :
          std::cout << "#TELECO_MESSAGE_MEDIA_VOLPLUS Group" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_VOLPLUS_ALL_SYNC :
          std::cout << "#TELECO_MESSAGE_MEDIA_VOLPLUS All" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_VOLMOINS :
          std::cout << "#TELECO_MESSAGE_MEDIA_VOLMOINS  Self" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_VOLMOINS_GROUP :
          std::cout << "#TELECO_MESSAGE_MEDIA_VOLMOINS Group" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_VOLMOINS_ALL_SYNC :
          std::cout << "#TELECO_MESSAGE_MEDIA_VOLMOINS All" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_MUTE :
          std::cout << "#TELECO_MESSAGE_MEDIA_MUTE  Self" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_MUTE_GROUP :
          std::cout << "#TELECO_MESSAGE_MEDIA_MUTE Group" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_MUTE_ALL_SYNC :
          std::cout << "#TELECO_MESSAGE_MEDIA_MUTE All" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_PAUSE :
          std::cout << "#TELECO_MESSAGE_MEDIA_PAUSE  Self" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_PAUSE_GROUP :
          std::cout << "#TELECO_MESSAGE_MEDIA_PAUSE Group" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_PLAY :
          std::cout << "#TELECO_MESSAGE_MEDIA_PLAY  Self" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_PLAY_GROUP :
          std::cout << "#TELECO_MESSAGE_MEDIA_PLAY Group" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_STOP :
          std::cout << "#TELECO_MESSAGE_MEDIA_STOP  Self" << std::endl;
          break;
        case TELECO_MESSAGE_MEDIA_STOP_GROUP :
          std::cout << "#TELECO_MESSAGE_MEDIA_STOP Group" << std::endl;
          break;
        default:
          //std::cout << "#TELECO_MESSAGE_UNKNOW" << std::endl;
          break;
          
      }
      break;
    case T_PUSHOK:
      std::cout << "#TELECO_PUSH_OK "<< valeur << std::endl;
      break;
    case T_REED:
      std::cout << "#TELECO_REED "<< valeur << std::endl;
      break;
    case T_FLOAT:
      std::cout << "#TELECO_FLOAT "<< valeur << std::endl;
      break;
    case T_INIT:
      if (valeur==0) needstart=1;
      break;
      
    default:
      break;
  }

  buff[0]= (char)(READCOMMAND+T_INIT);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  if (buff[1]==0){
    needstart=1;
  }

  return valeur;
}