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
  fprintf(stderr, "teleco - add teleco dnc\n");
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
  fprintf(stderr, "teleco - teleco start\n");
  uninit=0;
  setLedWarning(0);
  writeValue(T_INIT,1);
}

//reset remote
void Teleco::reset(){
  fprintf(stderr, "teleco - teleco reset\n");
  setLedWarning(1);
  writeValue(T_INIT,0);
  uninit=1;
}

//acces to led status
void Teleco::setLedOk(int val){
  writeValue(T_LEDOKVALUE,val);
}
void Teleco::setLedWarning(int val){
  writeValue(T_LEDRVALUE,(1-val));
}


//send info to the remote
void Teleco::sendString(char Str1[], char Str2[], int val){
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
  } else {
    fprintf(stderr, "teleco - cant send by lock\n");
  }
}

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
  fprintf(stderr, "teleco - read i %u",buff[1]);
  int address = buff[1];
  buff[0]= (char)(READCOMMAND+address);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  fprintf(stderr, "teleco - intterupt %u read %u\n",address,buff[1]);
  int valeur = buff[1];
  setLedWarning(0);
  switch (address) {
    case T_PUSHA:
      std::cout << "#TELECO_PUSH_A "<< valeur << std::endl;
      break;
    case T_PUSHB:
      std::cout << "#TELECO_PUSH_B "<< valeur << std::endl;
      break;
    case T_PUSHROTARY:
      switch (valeur){
        case 0:
          std::cout << "#TELECO_MESSAGE_UNKNOW" << std::endl;
          break;
        case 1:
          std::cout << "#TELECO_MESSAGE_PREVIOUSSCENE" << std::endl;
          break;
        case 2:
          std::cout << "#TELECO_MESSAGE_RESTARTSCENE" << std::endl;
          break;
        case 3:
          std::cout << "#TELECO_MESSAGE_NEXTSCENE" << std::endl;
          break;
        case 4:
          std::cout << "#TELECO_MESSAGE_BLINKGROUP" << std::endl;
          break;
        case 5:
          std::cout << "#TELECO_MESSAGE_RESTARTPY" << std::endl;
          break;
        case 6:
          std::cout << "#TELECO_MESSAGE_RESTARTWIFI" << std::endl;
          break;
        case 7:
          std::cout << "#TELECO_MESSAGE_UPDATESYS" << std::endl;
          break;
        case 8:
          std::cout << "#TELECO_MESSAGE_POWEROFF" << std::endl;
          if(localpoweroff==1){
            system ("sudo shutdown -h now");
          }
          break;
        case 9:
          std::cout << "#TELECO_MESSAGE_REBOOT" << std::endl;
          break;
        case 10:
          std::cout << "#TELECO_MESSAGE_TESTROUTINE" << std::endl;
          needtestroutine=1;
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
    case T_DISPLAY_LOCK:
      fprintf(stderr, "teleco - lock com\n");
      lockCom=valeur;
      break;
    case T_INIT:
      if (valeur==0) needstart=1;
      break;
      
    default:
      break;
  }

}