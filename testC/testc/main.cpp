//
//  main.cpp
//  testc
//
//  Created by SuperPierre on 10/12/2014.
//
//


#include "main.h"
#include "extSPI.h"


    // 8 Bits per word

int main (int argc, char * argv[]){
 
  extSPI mySPI;
  mySPI.initSPIHC595(2,21,1000000);
  mySPI.selectHC595csline(5);
  unsigned char buff[10];
  for (int i=0; i<10; i++) {
    buff[i]=i;
  }
  return mySPI.send(buff,10);

  
}

