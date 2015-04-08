//
//  main.cpp
//  testc
//
//  Created by SuperPierre on 10/12/2014.
//
//


#include "main.h"
#include "extSPI.h"

#include <stdio.h>
#include <fcntl.h>
#include <errno.h>

#include <wiringPi.h>
#include <wiringPiSPI.h>

#include "titreur.h"
#include "carte.h"
#include "teleco.h"

#include <iostream>
#include <fstream>
#include <cstring>
#include <sstream>
#include <string>


using namespace std;


Carte mycarte;
Teleco myteleco;
Titreur mytitreur;



void myInterruptCARTE (void) {
  fprintf(stderr, "intercarte\n");
  mycarte.readInterrupt();

}

void myInterruptTELECO(void) {
  fprintf(stderr, "interteleco\n");
  myteleco.readInterrupt();
  if (myteleco.fisrtView()) {
    myteleco.start();
    int tension = mycarte.checkTension();
    float v = tension;
    v=v/10;
    char mess[18];
    fprintf(stderr, "%u,%.1f\n",tension,v);
    sprintf(mess,"hello t=%.1fV",v);
    myteleco.sendString(mess);
  }

}

int parseInput(){
  string input;
  getline(cin, input);
  
  stringstream ss(input);
  string parsedInput;
  ss>>parsedInput;
   if ("initname"==parsedInput) {
     ss>>parsedInput;
    
    mytitreur.allLedOff();
    char buff[24];
     strncpy(buff, parsedInput.c_str(), sizeof(buff));
    //strcpy (buff,inputParse);
    mytitreur.text(0,0,buff);
    //mytitreur.text(0,0,parseInput);
    
  }
}


int main (int argc, char * argv[]){
  
  
  mytitreur.initTitreur(6,MODULE_24x16);

  mycarte.initCarte(PWM_LEDB,12);
  myteleco.initCarte();
  
  char text[] = "hello";
  mytitreur.text(0,0,text);


  wiringPiISR (20, INT_EDGE_RISING, &myInterruptCARTE) ;
  wiringPiISR (21, INT_EDGE_RISING, &myInterruptTELECO) ;

  cout << "inithardware" << endl;
  
  while(1){
    parseInput();


  }
  
  return 1;
  
}




/*
 extSPI mySPI;
 mySPI.initSPI();
 mySPI.addChipSelect(13,1000000);
 mySPI.addChipSelect(19,1000000);
 //mySPI.addChipSelectWithHC595Buffer(17,0,1000000);
 //mySPI.addChipSelectWithHC595Buffer(17,3,1000000);
 //mySPI.selectHC595csline(5);
 unsigned char buff[10];
 for (int i=0; i<10; i++) {
 buff[i]=i;
 }
 //mySPI.sendWithPause(0,buff,10);
 //mySPI.sendWithPause(1,buff,10);
 
 fprintf(stderr, "/n end send");
 mySPI.send(0,buff,10);
 mySPI.send(1,buff,10);
 //mySPI.send(2,buff,10);
 */


/*mycarte.writeValue(GYROMODE,1);
 mycarte.writeValue(LED10W1VALUE,255,0);
 delay(1000);
 mycarte.writeValue(LEDRVBSTROBSPEED,2);
 delay(5000);
 mycarte.writeValue(GYROSTROBSPEED,5);
 delay(50);
 mycarte.writeValue(LEDRVBSTROBSPEED,0);
 delay(5000);
 mycarte.writeValue(GYROSTROBSPEED,0);
 mycarte.writeValue(LED10W1VALUE,0,5);*/
/*mycarte.setGyro(GYRORIGHT,1000);
 mycarte.led10WValue(50);
 delay(1000);
 mycarte.led10WValue(255,5);
 delay(10000);
 mycarte.setGyro(GYROLEFT,200);
 mycarte.led10WValue(255,0,1000);
 delay(10000);
 mycarte.setGyro(GYROALLON,0,100);
 mycarte.led10WValue(0);*/

//mycarte.writeValue(LED10W1VALUE,22,25);
//delay(5);
//mycarte.readValue(LED10W1VALUE);
//delay(1000);
//mycarte.checkTension();
/*mycarte.writeValue(LED10W1VALUE,255,10);
 delay(15000);
 mycarte.writeValue(LED10W1VALUE,255,0);
 delay(1000);
 mycarte.writeValue(LED10W1VALUE,128,0);
 delay(1000);
 mycarte.writeValue(LED10W1VALUE,200,0);
 delay(1000);
 mycarte.writeValue(LED10W1VALUE,0,0);*/

//delay(300);
//mytitreur.allLedOn();
//delay(300);
//mytitreur.allLedOff();
//mytitreur.printScreen();

//mytitreur.testScreen();
//mytitreur.plot(2,2,1);
//mytitreur.plot(10,2,1);

//mytitreur.putChar(0,0,'B');
//mytitreur.putChar(7,0,'i');
//mytitreur.putChar(14,0,'s');
//mytitreur.plot(0,0,1);

