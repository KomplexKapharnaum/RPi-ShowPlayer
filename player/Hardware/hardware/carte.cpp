//
//  carte.cpp
//  testc
//
//  Created by SuperPierre on 20/03/2015.
//
//

#include "carte.h"

#include "extSPI.h"

#include <stdio.h>
#include <fcntl.h>
#include <errno.h>

#include <wiringPi.h>
#include <wiringPiSPI.h>
#include <iostream>
#include <string>




void Carte::initCarte(int _pwm_ledb_or_10w2, int _gamme_tension,int checkFloat){
  fprintf(stderr, "carte - add extension card dnc\n");
  SPIcarte.initSPI();
  SPIcarte.addChipSelect(13,1000000);
  gamme_tension=_gamme_tension;
  pwm_ledb_or_10w2=_pwm_ledb_or_10w2;
  wiringPiSetupGpio();
  GPIO_READ_BATT=25;
  GPIO_RESET=27;
  GPIO_RELAIS=26;
  GPIO_LED_GREEN=16;
  pinMode (GPIO_READ_BATT, OUTPUT);
  pinMode (GPIO_RESET, OUTPUT);
  pinMode (GPIO_RELAIS, OUTPUT);
  pinMode (GPIO_LED_GREEN, OUTPUT);
  digitalWrite (GPIO_RELAIS, LOW);
  digitalWrite (GPIO_RESET, HIGH);
  delay(1);
  digitalWrite (GPIO_RESET, LOW);
  delay(5);
  digitalWrite (GPIO_RESET, HIGH);
  delay(50);
  writeValue(VOLTAGEMODE,gamme_tension);
  checkTension();
  fprintf(stderr, "carte - tension initiale : %.1f mode : %uV\n", (float)tension/10, gamme_tension);
  writeValue(GYROSPEED,2);
  writeValue(BOARDCHECKFLOAT,checkFloat);
  writeValue(INTERRUPT,0);
  needStatusUpdate=0;
}


void Carte::writeValue(int valueType,int value, int fadetime){
  fprintf(stderr, "carte - writeValue %u : %u (f:%u) ", valueType,value,fadetime);
  int size;
  if(fadetime==0){size=2; }else {size=4;}
  unsigned char buff[5];
  buff[0]= (char)(WRITECOMMANDVALUE+valueType);
  buff[1]= (char)value;
  if(fadetime!=0){
    buff[2]= (char)(WRITECOMMANDFADE+valueType);
    buff[3]= (char)fadetime;
  }
  SPIcarte.send(0,buff,size);
}

int Carte::readValue(int valueType){
  fprintf(stderr, "carte - readValue %u = ", valueType);
  unsigned char buff[2];
  buff[0]= (char)(READCOMMAND+valueType);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  fprintf(stderr, "%u ",buff[1]);
  return buff[1];
}

int Carte::readInterrupt(){
  unsigned char buff[2];
  buff[0]= (char)(READCOMMAND+INTERRUPT);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  fprintf(stderr, "carte - read i %u\n",buff[1]);
  int address = buff[1];
  buff[0]= (char)(READCOMMAND+buff[1]);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  fprintf(stderr, "carte - read v %u\n",buff[1]);
  int valeur =buff[1];
  switch (address) {
      //@todo : faire un tableau et l'envoyer
    case PUSH1:
      std::cout << "#CARTE_PUSH_1 "<< valeur << std::endl;
      break;
    case PUSH2:
      std::cout << "#CARTE_PUSH_2 "<< valeur << std::endl;
      break;
    case PUSH3:
      std::cout << "#CARTE_PUSH_3 "<< valeur << std::endl;
      break;
    case FLOAT:
      std::cout << "#CARTE_FLOAT "<< valeur << std::endl;
      break;
    case UBATT:
        needStatusUpdate=1;
      break;
    default:
      break;
  }
  
}

float Carte::checkTension(){
  fprintf(stderr, "carte - checktension gpio high\n");
  digitalWrite (GPIO_READ_BATT, HIGH);
  delay(10);
  writeValue(UBATT,0);
  delay(5);
  tension = readValue(UBATT)+50;
  tension = tension/10;
  //digitalWrite (GPIO_READ_BATT, LOW);
  fprintf(stderr, "carte - get %.1fV\n",tension);
  needStatusUpdate=0;
  switch (gamme_tension) {
    case LIPO12:
      if(tension<10.8)
        std::cout << "#CARTE_TENSION_BASSE"<< std::endl;
      if(tension<10)
        std::cout << "#TELECO_MESSAGE_POWEROFF"<< std::endl;
      break;
    case LIFE12:
      if(tension<12.5)
        std::cout << "#CARTE_TENSION_BASSE"<< std::endl;
      if(tension<12)
        std::cout << "#TELECO_MESSAGE_POWEROFF"<< std::endl;
      break;
    case PB12:
      if(tension<12)
        std::cout << "#CARTE_TENSION_BASSE"<< std::endl;
      if(tension<11.5)
        std::cout << "#TELECO_MESSAGE_POWEROFF"<< std::endl;
      break;
    case LIPO24:
      if(tension<23.8)
        std::cout << "#CARTE_TENSION_BASSE"<< std::endl;
      if(tension<23)
        std::cout << "#TELECO_MESSAGE_POWEROFF"<< std::endl;
      break;
  }
  return tension;
}


void Carte::rgbValue(int r, int v, int b, int fadetime, int strob){
  if(strob!=0)fadetime=0; else writeValue(LEDRVBSTROBSPEED,0);
  writeValue(LEDRVALUE,r,fadetime);
  writeValue(LEDVVALUE,v,fadetime);
  writeValue(LEDBVALUE,b,fadetime);
  if(strob!=0){
    delay(1);
    writeValue(LEDRVBSTROBSPEED,strob/10);
  }
}

void Carte::led10WValue(int v, int fadetime, int strob){
  if(strob!=0)fadetime=0; else writeValue(LED10W1STROBSPEED,0);
  writeValue(LED10W1VALUE,v,fadetime);
  if(strob!=0){
    delay(1);
    writeValue(LED10W1STROBSPEED,strob/10);
  }
}

void Carte::setGyro(int mode, int speed, int strob){
  if(strob==0){
    writeValue(GYROSTROBSPEED,0);
    writeValue(GYROSPEED,speed/100);
    writeValue(GYROMODE,mode);
  }else{
    writeValue(GYROSTROBSPEED,strob/10);
  }
}

void Carte::setRelais(int val){
  fprintf(stderr, "carte - set relais %u",val);
  digitalWrite (GPIO_RELAIS, val);
}

void Carte::setledG(int val){
  fprintf(stderr, "carte - set led green %u",val);
  digitalWrite (GPIO_LED_GREEN, val);
}


Carte::~Carte(){
}