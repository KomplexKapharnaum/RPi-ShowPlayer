//
//  extSPI.cpp
//  testc
//
//  Created by SuperPierre on 10/12/2014.
//
//

#include "extSPI.h"

#include <stdio.h>
#include <fcntl.h>
#include <errno.h>
#include <linux/spi/spidev.h>
#include <sys/ioctl.h>
#include <time.h>
#include <sys/times.h>

#include <wiringPi.h>
#include <wiringPiSPI.h>
// for instal and build, follow the link
//https://projects.drogon.net/raspberry-pi/wiringpi/download-and-install/


#define GPIOCS  0
#define HC595   1

extSPI::extSPI(){
  init=0;
}

int extSPI::check(){
  if (!init) {
    fprintf(stderr, " you must init extSPI");
    return 1;
  }
  if (classmode==HC595 && selectedCSofHC595==-1) {
    fprintf(stderr, " you must select an active HC595 out defore send");
    return 1;
  }
  return 0;
}

void extSPI::initSPI(int csGPIOpin,int _spiSpeed){
  commonInit(_spiSpeed);
  cs=csGPIOpin;
  if(cs>1){
  wiringPiSetupGpio();
  pinMode (cs, OUTPUT) ;
  digitalWrite (cs, HIGH) ;
  }
  classmode=GPIOCS;
}

void extSPI::commonInit(int _spiSpeed){
  spiWRMode = 0;
  spiRDMode = 0;
  spiBitsPerWord = 8;
  spiSpeed = _spiSpeed;
  wiringPiSPISetup(0,spiSpeed);
  init=1;
}

void extSPI::initSPIHC595(int _nbHC595, int rckGPIOpin, int _spiSpeed){
  commonInit(_spiSpeed);
  nbmodule=_nbHC595;
  rck=rckGPIOpin;
  wiringPiSetupGpio();
  pinMode (rck, OUTPUT) ;
  digitalWrite (rck, LOW) ;
  classmode=HC595;
  selectedCSofHC595=-1;
}

int extSPI::send(unsigned char _byte){
  if(check())return -1;
  unsigned char buff[1];
  buff[0]=_byte;
  if(classmode==HC595) HC595select();
  else if(cs>1)digitalWrite (cs, LOW);
  wiringPiSPIDataRW (0, buff, 1);
  if(classmode==HC595) HC595unselect();
  else if(cs>1)digitalWrite (cs, HIGH);
  return 0;
}

int extSPI::send(unsigned char *_tab,int _len){
  if(check())return -1;
  unsigned char buff[_len];
  for (int i=0; i<_len; i++) {
    buff[i]=_tab[i];
  }
  if(classmode==HC595)HC595select();
  else if(cs>1)digitalWrite (cs, LOW);
  wiringPiSPIDataRW (0, buff, _len);
  if(classmode==HC595)HC595unselect();
  else if(cs>1)digitalWrite (cs, HIGH);
  return 0;
}


//cs is active thru HC595
//use mosi and sck two put data to hc595 and an aditional rck to latch value
void extSPI::HC595select(){
  int cs=nbmodule*8-selectedCSofHC595;
  unsigned long bitcs=0;
    bitcs = ~bitcs;
    bitcs ^=(1<<nbmodule*8>>cs);
  //fprintf(stderr, " %x", bitcs);
  unsigned char buff[nbmodule];
  for (int i=0; i<nbmodule; i++) {
    buff[(nbmodule-1-i)]=bitcs>>(8*i) & 0xFF;
  }
     // fprintf(stderr, " %x", buff[0]);
  //fprintf(stderr, " %x", buff[1]);
  wiringPiSPIDataRW (0, buff, nbmodule);
  digitalWrite (rck, HIGH);
  digitalWrite (rck, LOW) ;
}

void extSPI::HC595unselect(){
    unsigned char buff[nbmodule];
    for (int i=0; i<nbmodule; i++) {
      buff[i]=0xFF;
    }
    wiringPiSPIDataRW (0, buff, nbmodule);
    digitalWrite (rck, HIGH);
    digitalWrite (rck, LOW) ;
}

void extSPI::selectHC595csline(int _selectedCSofHC595){
  selectedCSofHC595=_selectedCSofHC595;
}













