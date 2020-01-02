//
//  extSPI.cpp
//  testc
//
//  Created by SuperPierre on 10/12/2014.
//
//

#include "extSPI.h"
#include <stdint.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <fcntl.h>
#include <errno.h>
#include <linux/spi/spidev.h>
#include <sys/ioctl.h>
#include <time.h>
#include <sys/times.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include <wiringPi.h>
#include <wiringPiSPI.h>
// for instal and build, follow the link
//https://projects.drogon.net/raspberry-pi/wiringpi/download-and-install/

#include <string>



extSPI::extSPI(){
  init=0;
}


int extSPI::check(){
  if (!init) {
    fprintf(stderr, "extspi -  you must init extSPI");
    return 1;
  }
  return 0;
}


void extSPI::initSPI(int speed){
  commonInit(speed);
  nbmodule=1;
  fprintf(stderr, "extspi - init base speed %u ok \n",speed);
}

void extSPI::commonInit(int _spiSpeed){
  spiWRMode = 0;
  spiRDMode = 0;
  spiBitsPerWord = 8;
  spifile=wiringPiSPISetup(0,_spiSpeed);
  //define 244
  wiringPiSetupGpio();
  GPIO_LED=12;
  pinMode (GPIO_LED, OUTPUT) ;
  digitalWrite (GPIO_LED, LOW);
  GPIO_244_ENABLE = 5; //define by electronic (do not forget it's inverted line)
  pinMode (GPIO_244_ENABLE, OUTPUT) ;
  digitalWrite (GPIO_244_ENABLE, LOW);
  init=1;
  csmax=0;
}

void extSPI::addChipSelect(int GPIO,int speed){
  chipSelect[csmax].GPIO=GPIO;
  chipSelect[csmax].speed=speed;
  chipSelect[csmax].HC595=-1;
  pinMode (chipSelect[csmax].GPIO, OUTPUT) ;
  digitalWrite (chipSelect[csmax].GPIO, HIGH);
  csmax++;
  fprintf(stderr, "extspi - add direct gpio cs, gpio=%u, speed=%u\n",GPIO,speed);
  releaseSelect();
}

void extSPI::addChipSelectWithHC595Buffer(int RCK, int HC595,int speed){
  chipSelect[csmax].GPIO=RCK;
  chipSelect[csmax].speed=speed;
  chipSelect[csmax].HC595=HC595;
  pinMode (chipSelect[csmax].GPIO, OUTPUT) ;
  digitalWrite (chipSelect[csmax].GPIO, LOW);
  csmax++;
  fprintf(stderr, "extspi - add hc595 cs, RCK=%u, HC595=%u, speed=%u\n",RCK,HC595, speed);
  releaseSelect();
}
/*
void extSPI::initSPIHC595(int _nbHC595, int rckGPIOpin, int _spiSpeed){
  commonInit(_spiSpeed);
  nbmodule=_nbHC595;
  rck=rckGPIOpin;
  wiringPiSetupGpio();
  pinMode (rck, OUTPUT) ;
  digitalWrite (rck, LOW) ;
  classmode=HC595;
  selectedCSofHC595=-1;
}*/


int extSPI::send(int _selectedChip, unsigned char _byte){
  selectedChip=_selectedChip;
  if(check())return -1;
  unsigned char buff[1];
  buff[0]=_byte;
  //if(classmode==HC595) HC595select();
  //else if(cs>1)digitalWrite (cs, LOW);
  activeCS();
  wiringPiSPIDataRW (0, buff, 1);
  inactiveCS();
  //if(classmode==HC595) HC595unselect();
  //else if(cs>1)digitalWrite (cs, HIGH);
  return buff[0];
}


int extSPI::send(int _selectedChip, unsigned char *_tab,int _len){
  selectedChip=_selectedChip;
  if(check())return -1;
  
  //if(classmode==HC595)HC595select();
  //else if(cs>1)digitalWrite (cs, LOW);
  activeCS();
  wiringPiSPIDataRW (0, _tab, _len);
  inactiveCS();
  //if(classmode==HC595)HC595unselect();
  //else if(cs>1)digitalWrite (cs, HIGH);
  
  return 0;
}

int extSPI::sendWithPause(int _selectedChip, unsigned char *_tab,int _len){
  selectedChip=_selectedChip;
  if(check())return -1;
  activeCS();
  unsigned char buff[1];
  for (int i=0; i<_len; i++) {
    buff[0]=_tab[i];
    wiringPiSPIDataRW (0, buff, 1);
    //fprintf(stderr, "swp %u->%u ",_tab[i],buff[0]);
    _tab[i]= buff[0];
    delay(2);
    //nanosleep((struct timespec[]){{0, 20000}}, NULL);
    //nanosleep(&tim);
  }
  //fprintf(stderr, "\n");
  inactiveCS();
  
  return 0;
}




//cs is active thru HC595
//use mosi and sck two put data to hc595 and an aditional rck to latch value
void extSPI::HC595select(){
    //fprintf(stderr, "extspi - active hc95 %u, prev=%u, keep=%u\n",chipSelect[selectedChip].HC595, hc595activated, keepSelect);
    hc595activated=chipSelect[selectedChip].HC595;
    int cs=nbmodule*8-chipSelect[selectedChip].HC595;
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
  digitalWrite (chipSelect[selectedChip].GPIO, HIGH);
}

/*
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
}*/



//cs is active thru 74ACT244
void extSPI::activeCS(){
  //fprintf(stderr, "extspi - active spi, speed=%u for %u - gpio%u\n",chipSelect[selectedChip].speed,selectedChip, chipSelect[selectedChip].GPIO);
  //try only change speed
  //int fd=wiringPiSPISetupSpeed(spifile,chipSelect[selectedChip].speed);
  if(lastSpeed!=chipSelect[selectedChip].speed){
    close(spifile);
    spifile = wiringPiSPISetup(0,chipSelect[selectedChip].speed);
    lastSpeed=chipSelect[selectedChip].speed;
  }
  //this do not work beacause open file each time
  if(chipSelect[selectedChip].GPIO!=csactivated || hc595activated!=chipSelect[selectedChip].HC595 || keepSelect==0){
    //fprintf(stderr, "extspi - active gpio %u, prev %u, keep=%u\n",chipSelect[selectedChip].GPIO,csactivated,keepSelect);
    csactivated=chipSelect[selectedChip].GPIO;
    //inactiveCS();
    digitalWrite (GPIO_LED, HIGH);
    digitalWrite (GPIO_244_ENABLE, HIGH);
    if(chipSelect[selectedChip].HC595==-1) digitalWrite (chipSelect[selectedChip].GPIO, LOW);
    else HC595select();
  }
}


void extSPI::inactiveCS(){
  //fprintf(stderr, "extspi - unactive spi, speed=%u for %u - gpio%u\n",chipSelect[selectedChip].speed,selectedChip, chipSelect[selectedChip].GPIO);
  if(keepSelect==0){
  for(int i=0;i<csmax;i++){
    if(chipSelect[i].HC595==-1)digitalWrite (chipSelect[i].GPIO, HIGH);
    else digitalWrite (chipSelect[i].GPIO, LOW);
  }
  digitalWrite (GPIO_244_ENABLE, LOW);
  digitalWrite (GPIO_LED, LOW);
  }
}

void extSPI::setkeepSelect(){
  keepSelect=1;
}

void extSPI::releaseSelect(){
  keepSelect=0;
  hc595activated =-1;
  csactivated=-1;
  inactiveCS();
}











