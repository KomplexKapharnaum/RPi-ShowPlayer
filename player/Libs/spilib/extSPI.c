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


extSPI::extSPI(int _cs,int _spiSpeed){
  errFlag=0;
  spiWRMode = 0;
  spiRDMode = 0;
  spiBitsPerWord = 8;
  spiSpeed = _spiSpeed;
  
  cs=_cs;
  if(cs>1){
  wiringPiSetupGpio();
  pinMode (cs, OUTPUT) ;
  digitalWrite (cs, HIGH) ;
  }
  
  wiringPiSPISetup(0,spiSpeed);

}



int extSPI::send(unsigned char _byte){
  
  unsigned char buff[32];
  for (int i=0; i<32; i++) {
    buff[i]=_byte;
  }
  
  if(cs>1)digitalWrite (cs, LOW) ;
  wiringPiSPIDataRW (0, buff, 32);
  if(cs>1)digitalWrite (cs, HIGH) ;
  
}


//cs is active thru HC595
//use mosi and sck two put data to hc595 and an aditional rck to latch value

extSPIwithHCT595::extSPIwithHCT595(int _nbmodule, int _rck, int _spiSpeed){
  spiSpeed=_spiSpeed;
  nbmodule=_nbmodule;
  rck=_rck;
  wiringPiSetupGpio();
  pinMode (rck, OUTPUT) ;
  digitalWrite (rck, LOW) ;
  mySPI= extSPI(0,spiSpeed);
  
}

void extSPIwithHCT595::select(int cs){
    unsigned long bitcs=0;
    bitcs = ~bitcs;
    bitcs ^=(1<<nbmodule*8>>cs);
  unsigned char buff[nbmodule];
  for (int i=0; i<nbmodule; i++) {
    buff[i]=0;
    for (int j=0; j<8; j++) {
      buff[i]|=(bitcs>>(i*8+j)>>(7-j));
    }
    
  }
  wiringPiSPIDataRW (0, buff, nbmodule);
  
  digitalWrite (rck, HIGH);
  digitalWrite (rck, LOW) ;
}

void extSPIwithHCT595::unselect(){
    unsigned char buff[nbmodule];
    for (int i=0; i<nbmodule; i++) {
      buff[i]=0xFF;
    }
    wiringPiSPIDataRW (0, buff, nbmodule);
    digitalWrite (rck, HIGH);
    digitalWrite (rck, LOW) ;
}

int extSPIwithHCT595::send(unsigned char _byte, int cs){
  select(cs);
  
  unsigned char buff[32];
  for (int i=0; i<32; i++) {
    buff[i]=_byte;
  }
  
  if(cs>1)digitalWrite (cs, LOW) ;
  wiringPiSPIDataRW (0, buff, 32);
  if(cs>1)digitalWrite (cs, HIGH) ;

  unselect();
  
  
}









