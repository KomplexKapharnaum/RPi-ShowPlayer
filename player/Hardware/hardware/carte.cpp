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

#include <sys/time.h>
#include <unistd.h>
#include <inttypes.h>



//init carte
void Carte::initCarte(int _pwm_ledb_or_10w2, int _gamme_tension,int checkFloat){
  fprintf(stderr, "\n\x1b[32mcarte - add extension card dnc\n\x1b[0m");
  SPIcarte.initSPI();
  SPIcarte.addChipSelect(13,500000);
  gamme_tension=_gamme_tension;
  pwm_ledb_or_10w2=_pwm_ledb_or_10w2;
  wiringPiSetupGpio();
  GPIO_READ_BATT=25;
  GPIO_RESET=27;
  GPIO_RELAIS=26;
  GPIO_LED_GREEN=16;
  GPIO_INTERRUPT=20;
  pinMode (GPIO_READ_BATT, OUTPUT);
  pinMode (GPIO_RESET, OUTPUT);
  pinMode (GPIO_RELAIS, OUTPUT);
  pinMode (GPIO_LED_GREEN, OUTPUT);
  pinMode (GPIO_INTERRUPT, INPUT);
  digitalWrite (GPIO_RELAIS, LOW);
  fprintf(stderr, "carte - reset atmega and wait ");
  digitalWrite (GPIO_RESET, HIGH);
  delay(1);
  digitalWrite (GPIO_RESET, LOW);
  delay(5);
  digitalWrite (GPIO_RESET, HIGH);
  while (digitalRead(GPIO_INTERRUPT)==LOW) {
    fprintf(stderr, ".");
    usleep(5000);
  }
  fprintf(stderr, "\n");
  writeValue(VOLTAGEMODE,gamme_tension);
  writeValue(GYROSPEED,2);
  writeValue(BOARDCHECKFLOAT,checkFloat);
  writeValue(INTERRUPT,0);
  needStatusUpdate=0;
  count_tensionbasse=0;
  count_tensioncoupure=0;
  core_version = readValue(VERSION);
  fprintf(stderr, "\n\x1b[32mcarte - core version : %u\n\x1b[0m",core_version);
}


//write value in carte register
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
  delay(5);
}

//read value from carte register
int Carte::readValue(int valueType){
  //fprintf(stderr, "carte - readValue %u = ", valueType);
  unsigned char buff[2];
  buff[0]= (char)(READCOMMAND+valueType);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  //fprintf(stderr, "%u \n",buff[1]);
  return buff[1];
}

/* TIME MEASURE */
unsigned long long cmstime() {
	struct timeval tv;

	gettimeofday(&tv, NULL);

	unsigned long long millisecondsSinceEpoch =
	    (unsigned long long)(tv.tv_sec) * 1000 +
	    (unsigned long long)(tv.tv_usec) / 1000;

	return millisecondsSinceEpoch;
}

//read carte interrupt and out corresponding message
int Carte::readInterrupt(){
  unsigned char buff[2];
  buff[0]= (char)(READCOMMAND+INTERRUPT);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  //fprintf(stderr, "carte - read i %u\n",buff[1]);
  int address = buff[1];
  if (address<POWERDOWN && address>INTERRUPT) {
  buff[0]= (char)(READCOMMAND+buff[1]);
  buff[1]=0;
  SPIcarte.sendWithPause(0,buff,2);
  fprintf(stderr, "carte - interrupt %u read %u\n",address,buff[1]);
  int valeur;
  valeur = buff[1];
  switch (address) {
      //@todo : faire un tableau et l'envoyer
    case PUSH1:
      //std::cout << "#CARTE_PUSH_1 "<< valeur << std::endl;
      if (valeur==1){
        startchrono = cmstime();
        checkchrono = true;
      }
      if (checkchrono && valeur==0){
        if(cmstime()-startchrono>2000 && cmstime()-startchrono<10000) {
          std::cout << "#CARTE_PUSH_11 1" << std::endl;
          count_long_push++;
          // you need to make 5 successive long push for reboot
          if(count_long_push>4) system ("sudo reboot");
          break;
        }
        std::cout << "#CARTE_PUSH_1 1" << std::endl;
        count_long_push=0;
      }
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
  return valeur;
  }else {
    fprintf(stderr, ".");
  }
  return 0;
}

//read tension from carte
float Carte::checkTension(){
  //fprintf(stderr, "carte - checktension gpio high\n");
  //analog in from atmega is after a mosfet under rpi control
  //not useless, change in V2
  digitalWrite (GPIO_READ_BATT, HIGH);
  delay(10);
  writeValue(UBATT,0);
  delay(60);
  tension = readValue(UBATT)+50;
  tension = tension/10;
  //strange behaviour
  //digitalWrite (GPIO_READ_BATT, LOW);
  //fprintf(stderr, "carte - checktension gpio low\n");
  fprintf(stderr, "carte - get %.1fV\n",tension);
  std::cout << "#CARTE_TENSION " << tension << std::endl;
  needStatusUpdate=0;
  switch (gamme_tension) {
    case LIPO12:
      if(tension>=10.8) count_tensionbasse=0;
      if(tension<10.8) count_tensionbasse++;
      if(tension>=10) count_tensioncoupure=0;
      if(tension<10) count_tensioncoupure++;
      break;
    case LIFE12:
      if(tension<12.5) count_tensionbasse++;
      if(tension<12) count_tensioncoupure++;
      if(tension>=12.5) count_tensionbasse=0;
      if(tension>=12) count_tensioncoupure=0;
      break;
    case PB12:
      if(tension<12) count_tensionbasse++;
      if(tension<11.5) count_tensioncoupure++;
      if(tension>=12) count_tensionbasse=0;
      if(tension>=11.5) count_tensioncoupure=0;
      break;
    case LIPO24:
      if(tension<23.8) count_tensionbasse++;
      if(tension<23) count_tensioncoupure++;
      if(tension>=23.8) count_tensionbasse=0;
      if(tension>=23) count_tensioncoupure=0;
      break;
  }
  if (count_tensionbasse>1) {
    std::cout << "#CARTE_TENSION_BASSE"<< std::endl;
  }
  if (count_tensioncoupure>1) {
    std::cout << "#CARTE_MESSAGE_POWEROFF"<< std::endl;
  }
  return tension;
}

//short for rgb led register
void Carte::rgbValue(int r, int v, int b, int fadetime, int strob){
  if(strob!=0)fadetime=0; else writeValue(LEDRVBSTROBSPEED,0);
  writeValue(LEDRVALUE,r,fadetime);
  writeValue(LEDVVALUE,v,fadetime);
  writeValue(LEDBVALUE,b,fadetime);
  if(strob!=0){
    writeValue(LEDRVBSTROBSPEED,strob/10);
  }
}

//short for led10W register
void Carte::led10WValue(int v, int fadetime, int strob){
  if(strob!=0)fadetime=0; else writeValue(LED10W1STROBSPEED,0);
  writeValue(LED10W1VALUE,v,fadetime);
  if(strob!=0){
    writeValue(LED10W1STROBSPEED,strob/10);
  }
}

//short for gyro flex led register
void Carte::setGyro(int mode, int speed, int strob){
  if(strob==0){
    writeValue(GYROSTROBSPEED,0);
    writeValue(GYROSPEED,speed/100);
    writeValue(GYROMODE,mode);
  }else{
    writeValue(GYROSTROBSPEED,strob/10);
  }
}

//short for relais rpi gpio
void Carte::setRelais(int val){
  fprintf(stderr, "carte - set relais %u",val);
  digitalWrite (GPIO_RELAIS, val);
}

//short for led green rpi gpio
void Carte::setledG(int val){
  fprintf(stderr, "carte - set led green %u",val);
  digitalWrite (GPIO_LED_GREEN, val);
}

void Carte::setManualLightMode(int val){
  if(val==1){
    writeValue(BOARDMODE,0);
    fprintf(stderr, "carte - manual light activated (by default) \n");
  }else{
    writeValue(BOARDMODE,1);
    fprintf(stderr, "carte - manual light desactivated \n");
  }
  
}


Carte::~Carte(){
}