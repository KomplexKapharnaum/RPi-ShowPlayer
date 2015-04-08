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
  uninit=1;
}

int Teleco::fisrtView(){
  return uninit;
}

void Teleco::start(){
  fprintf(stderr, "teleco start\n");
  uninit=0;
  writeValue(T_LEDRVALUE,1);
}


void Teleco::sendString(char Str1[]){
  fprintf(stderr, "send %s\n",Str1);
  unsigned char buff[17];
  buff[0]= (char)(WRITECOMMANDVALUE+T_STRING);
  for(int i=0;i<16;i++){
    buff[i+1]= *(Str1+i);
  }
  SPIcarte.send(0,buff,17);
}

int Teleco::readInterrupt(){
  unsigned char buff[2];
  buff[0]= (char)(READCOMMAND+T_INTERRUPT);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  fprintf(stderr, "read i %u\n",buff[1]);
  int address = buff[1];
  //if (address==0) {
  //  uninit=0;
  //}
  buff[0]= (char)(READCOMMAND+address);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  fprintf(stderr, "read v %u\n",buff[1]);
  int valeur = buff[1];
  switch (address) {
    case T_PUSHA:
      std::cout << "teleco_pushA "<< valeur << std::endl;
      break;
    case T_PUSHB:
      std::cout << "teleco_pushB "<< valeur << std::endl;
      break;
    case T_PUSHROTARY:
      std::cout << "teleco_pushRotary "<< valeur << std::endl;
      break;
    case T_PUSHOK:
      std::cout << "teleco_pushOK "<< valeur << std::endl;
      break;
    case T_REED:
      std::cout << "teleco_reed "<< valeur << std::endl;
      break;
    case T_FLOAT:
      std::cout << "teleco_float "<< valeur << std::endl;
      break;
      
    default:
      break;
  }
}