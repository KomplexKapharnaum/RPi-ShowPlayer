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



void Teleco::initCarte(char pow){
  localpoweroff=pow;
  fprintf(stderr, "teleco - add teleco dnc\n");
  SPIcarte.initSPI();
  SPIcarte.addChipSelect(19,500000);
}

int Teleco::fisrtView(){
  return uninit;
}

void Teleco::start(){
  fprintf(stderr, "teleco - teleco start\n");
  uninit=0;
  writeValue(T_LEDRVALUE,1);
}

void Teleco::reset(){
  fprintf(stderr, "teleco - teleco reset\n");
  setLedWarning(1);
  writeValue(T_INIT,0);
}

void Teleco::setLedOk(int val){
  writeValue(T_LEDOKVALUE,val);
}

void Teleco::setLedWarning(int val){
  writeValue(T_LEDRVALUE,val);
}


void Teleco::sendInfo(char Str1[], char Str2[],char Str3[], char Str4[]){
  //fprintf(stderr, "teleco send infos : %s / %s / %s / %s\n",Str1,Str2, Str3, Str4);
  unsigned char buff[68];
  buff[0]= (char)(WRITECOMMANDVALUE+T_STRING);
  for(int i=0;i<16;i++){
    buff[i+1]= *(Str1+i);
  }
  for(int i=0;i<16;i++){
    buff[i+17]= *(Str2+i);
  }
  for(int i=0;i<16;i++){
    buff[i+33]= *(Str3+i);
  }
  for(int i=0;i<16;i++){
    buff[i+49]= *(Str4+i);
  }
  fprintf(stderr, "teleco - teleco send infos : %s\n",buff);
  SPIcarte.send(0,buff,68);
}

void Teleco::sendPopUp(char Str1[], char Str2[]){
  setLedWarning(1);
  unsigned char buff[35];
  buff[0]= (char)(WRITECOMMANDVALUE+T_POPUP);
  for(int i=0;i<16;i++){
    buff[i+1]= *(Str1+i);
  }
  for(int i=0;i<16;i++){
    buff[i+17]= *(Str2+i);
  }
  fprintf(stderr, "teleco - teleco send popup : %s\n",buff);
  SPIcarte.send(0,buff,34);
  setLedWarning(0);
}


int Teleco::readInterrupt(){
  setLedWarning(1);
  unsigned char buff[2];
  buff[0]= (char)(READCOMMAND+T_INTERRUPT);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  fprintf(stderr, "teleco - read i %u\n",buff[1]);
  int address = buff[1];
  buff[0]= (char)(READCOMMAND+address);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  fprintf(stderr, "teleco - read v %u\n",buff[1]);
  int valeur = buff[1];
  switch (address) {
    case T_PUSHA:
      std::cout << "#TELECO_PUSH_A "<< valeur << std::endl;
      break;
    case T_PUSHB:
      std::cout << "#TELECO_PUSH_B "<< valeur << std::endl;
      break;
    case T_PUSHROTARY:
      switch (valeur){
        case 250:
          std::cout << "#TELECO_GET_INFO" << std::endl;
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
          std::cout << "#TELECO_MESSAGE_POWEROFF" << std::endl;
          if(localpoweroff==1){
            system ("sudo shutdown -h now");
          }
          break;
        case 6:
          std::cout << "#TELECO_MESSAGE_REBOOT" << std::endl;
          break;
        case 7:
          std::cout << "#TELECO_MESSAGE_TESTROUTINE" << std::endl;
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
      
    default:
      uninit=1;
      break;
  }
  setLedWarning(0);
}