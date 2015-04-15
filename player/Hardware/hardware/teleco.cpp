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

#include <cstring>
#include <sstream>
#include <string>

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


void Teleco::sendString(std::string messages){
  unsigned char buff[68];
  buff[0]= (char)(WRITECOMMANDVALUE+T_STRING);
  replace( messages.begin(), messages.end(), ' ', '_');
  replace( messages.begin(), messages.end(), '$', ' ');
  std::stringstream ss(messages);
  std::string parsedInput;
  char buffline[17];
  int count =0;
  while (ss>>parsedInput){
    replace( parsedInput.begin(), parsedInput.end(), '_', ' ');
    strncpy(buffline, parsedInput.c_str(), sizeof(buff));
    for(int i=0;i<16;i++){
      buff[i+count*16+1]= *(buffline+i);
    }
    count++;
  }
  SPIcarte.send(0,buff,68);
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
}