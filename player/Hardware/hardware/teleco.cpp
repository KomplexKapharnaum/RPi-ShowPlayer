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

void Teleco::initCarte(){
  fprintf(stderr, "add teleco dnc\n");
  SPIcarte.initSPI();
  SPIcarte.addChipSelect(19,500000);
}

int Teleco::fisrtView(){
  return uninit;
}

void Teleco::start(){
  fprintf(stderr, "teleco start\n");
  uninit=0;
  writeValue(T_LEDRVALUE,1);
}


void Teleco::sendString(char Str1[], int line){
  fprintf(stderr, "send %s\n",Str1);
  unsigned char buff[18];
  buff[0]= (char)(WRITECOMMANDVALUE+T_STRING);
  if (line==2)buff[1]='2';
  if (line==1)buff[1]='1';
  if (line==0)buff[0]='0';
  for(int i=0;i<16;i++){
    buff[i+2]= *(Str1+i);
  }
  SPIcarte.send(0,buff,18);
}

int Teleco::readInterrupt(){
  unsigned char buff[2];
  buff[0]= (char)(READCOMMAND+T_INTERRUPT);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  fprintf(stderr, "read i %u\n",buff[1]);
  int address = buff[1];
  buff[0]= (char)(READCOMMAND+address);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  fprintf(stderr, "read v %u\n",buff[1]);
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
          //char menu[T_NBMENU][16] = {"startscene","restartscene","nextscene","blinkgroup","poweroff","testroutine"};
        case 1:
          std::cout << "#TELECO_MESSAGE startscene" << std::endl;
          break;
        case 2:
          std::cout << "#TELECO_MESSAGE restartscene" << std::endl;
          break;
        case 3:
          std::cout << "#TELECO_MESSAGE nextscene" << std::endl;
          break;
        case 4:
          std::cout << "#TELECO_MESSAGE blinkgroup" << std::endl;
          break;
        case 5:
          std::cout << "#TELECO_MESSAGE poweroff" << std::endl;
          break;
        case 6:
          std::cout << "#TELECO_MESSAGE testroutine" << std::endl;
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
}