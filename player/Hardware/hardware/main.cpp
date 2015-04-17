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
#include <algorithm>

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>


using namespace std;

string carte_name;
string carte_ip;
string version_py="-";
string version_c="0.2";
string status="-";
string popup1,popup2;
string voltage="-";
int init=0;

Carte mycarte;
Teleco myteleco;
Titreur mytitreur;



void myInterruptCARTE (void) {
  fprintf(stderr, "intercarte\n");
  mycarte.readInterrupt();

}

void sendStatusTeleco(){
  int tension = mycarte.checkTension();
  float v = tension;
  v=v/10;
  char mess1[17];
  char mess2[17];
  char mess3[17];
  char mess4[17];
  delay(10);
  sprintf(mess1,"stat=%s",status.c_str());
  sprintf(mess2,"pyt%s C%s",version_py.c_str(),version_c.c_str());
  sprintf(mess3,"%s",carte_name.c_str());
  sprintf(mess4,"%s %.1fV",carte_ip.c_str(),v);
  myteleco.sendInfo(mess1,mess2,mess3,mess4);
}

void beforekill(int signum)
{
    
  mycarte.setGyro(0, 200);
  mycarte.led10WValue(0);
  mycarte.rgbValue(0,0,0);
  mycarte.setRelais(0);
  mytitreur.allLedOff();
  status="noC";
  myteleco.reset();
  fprintf(stderr, "bye bye\n");
  exit(signum);
}

void myInterruptTELECO(void) {
  fprintf(stderr, "interteleco\n");
  if (myteleco.fisrtView()){
    delay(200);
    fprintf(stderr, "delaypass\n");
  }
  if (digitalRead(21)==HIGH) {
    fprintf(stderr, "reel interrupt\n");
    myteleco.readInterrupt();
    if (myteleco.fisrtView()) {
      myteleco.start();
      sendStatusTeleco();
    }
  }
}



void testRoutine(int n){
  string msg;
  char buff[24];
  msg="test";
  strncpy(buff, msg.c_str(), sizeof(buff));
  mytitreur.text(0,0,buff);
  while (n>0){
    mycarte.rgbValue(255,0,0,0,0);
    delay(1000);
    mycarte.rgbValue(0,255,0,0,0);
    delay(1000);
    mycarte.rgbValue(0,0,255,0,0);
    delay(1000);
    mycarte.rgbValue(0,0,0,0,0);
    delay(10);
    mycarte.led10WValue(255,3,0);
    delay(3000);
    mycarte.led10WValue(0,0,0);
    delay(10);
    mycarte.setGyro(2,200,0);
    delay(3000);
    mycarte.setGyro(0,0,0);
    n--;
  }
  msg="end";
  strncpy(buff, msg.c_str(), sizeof(buff));
  mytitreur.text(0,0,buff);
  
}


int parseInput(){
  string input;
  getline(cin, input);
  fprintf(stderr, "\nGETCOMMAND : %s\n",input.c_str());
  stringstream ss(input);
  string parsedInput;
  ss>>parsedInput;
  if (init==0){
    if ("initconfig"==parsedInput) {
      while (ss>>parsedInput){
        if ("-titreurNbr"==parsedInput){
          int nbmodule;
          ss>>nbmodule;
          mytitreur.initTitreur(nbmodule,MODULE_24x16);
        }
        if ("-carteVolt"==parsedInput){
          ss>>parsedInput;
          voltage=parsedInput;
          if(voltage=="-")mycarte.initCarte(PWM_LEDB,0);
          else if(voltage=="life12")mycarte.initCarte(PWM_LEDB,13);
          else if(voltage=="lipo12")mycarte.initCarte(PWM_LEDB,11);
          else if(voltage=="pb12")mycarte.initCarte(PWM_LEDB,11);
          else if(voltage=="lipo24")mycarte.initCarte(PWM_LEDB,27);
          else if(voltage=="life24")mycarte.initCarte(PWM_LEDB,26);
          else if(voltage=="pb24")mycarte.initCarte(PWM_LEDB,24);
          else mycarte.initCarte(PWM_LEDB,0);
        }
        if ("-name"==parsedInput){
          ss>>parsedInput;
          carte_name=parsedInput;
        }
        if ("-ip"==parsedInput){
          ss>>parsedInput;
          carte_ip=parsedInput;
        }
        if ("-version"==parsedInput){
          ss>>parsedInput;
          version_py=parsedInput;
        }
        if ("-status"==parsedInput){
          ss>>parsedInput;
          status=parsedInput;
        }
      }
      init=1;
      
      mytitreur.allLedOff();
      char buff[24];
      strncpy(buff, carte_name.c_str(), sizeof(buff));
      mytitreur.text(0,0,buff);
      strncpy(buff, carte_ip.c_str(), sizeof(buff));
      mytitreur.text(0,8,buff);
    }else{
      fprintf(stderr, "error you must init first\ninitconfig -titreurNbr [int] -carteVolt [int] -name [string] -ip [string]\n");
    }
    if ("S"==parsedInput) {
      fprintf(stderr, "overpass standard debug init\n");
      mytitreur.initTitreur(6,MODULE_24x16);
      mycarte.initCarte(PWM_LEDB,12);
      carte_name="TEST STAND";
      carte_ip="2.0.2.XXX";
      init=1;
      mytitreur.putChar(0,0,'S');
    }
    
  }else{
    
    if ("info"==parsedInput) {
      while (ss>>parsedInput){
        if ("-version"==parsedInput){
          ss>>parsedInput;
          version_py=parsedInput;
        }
        if ("-status"==parsedInput){
          ss>>parsedInput;
          status=parsedInput;
        }
      }
      sendStatusTeleco();
    }
    
    if ("popup"==parsedInput) {
      while (ss>>parsedInput){
        if ("-line1"==parsedInput){
          ss>>parsedInput;
          replace( parsedInput.begin(), parsedInput.end(), '_', ' ');
          popup1=parsedInput;
        }
        if ("-line2"==parsedInput){
          ss>>parsedInput;
          replace( parsedInput.begin(), parsedInput.end(), '_', ' ');
          popup2=parsedInput;
        }
        if ("-clear"==parsedInput){
          popup1=" ";
          popup2=" ";
        }
      }
      char mess1[17];
      char mess2[17];
      sprintf(mess1,"%s",popup1.c_str());
      sprintf(mess2,"%s",popup2.c_str());
      myteleco.sendPopUp(mess1,mess2);
    }


    if ("initconfig"==parsedInput) {
      fprintf(stderr, "error already init\n");
    }
    //init ok, traitement des autres commandes
    if ("texttitreur"==parsedInput) {
      mytitreur.allLedOff();
      while (ss>>parsedInput){
        char buff[mytitreur.charbyline()];
        if ("-line1"==parsedInput){
          ss>>parsedInput;
          replace( parsedInput.begin(), parsedInput.end(), '_', ' ');
          strncpy(buff, parsedInput.c_str(), sizeof(buff));
          mytitreur.text(0,0,buff);
        }
        if ("-line2"==parsedInput){
          ss>>parsedInput;
          replace( parsedInput.begin(), parsedInput.end(), '_', ' ');
          strncpy(buff, parsedInput.c_str(), sizeof(buff));
          mytitreur.text(0,8,buff);
        }
        if ("-allon"==parsedInput){
          mytitreur.allLedOn();
        }
        if ("-alloff"==parsedInput){
          mytitreur.allLedOff();
        }
        if ("-scroll"==parsedInput){
          // todo mytitreur.scroll();
        }
      }
    }// end textTitreur
    
    if ("setlight"==parsedInput) {
      int fade=0;
      int strob=0;
      while (ss>>parsedInput){
        char buff[mytitreur.charbyline()];
        if ("-rgb"==parsedInput){
          int r,g,b;
          ss>>r; ss>>g; ss>>b;
          mycarte.rgbValue(r,g,b,fade,strob);
        }
        if ("-10w1"==parsedInput){
          int v;
          ss>>v;
          mycarte.led10WValue(v,fade,strob);
        }
        if ("-10w2"==parsedInput){
          // todo led10W2Value();
        }
        if ("-fade"==parsedInput){
          ss>>fade;
        }
        if ("-strob"==parsedInput){
          ss>>strob;
        }
      }
    }// end setlight
    
    if ("setgyro"==parsedInput) {
      int speed=350;
      int strob=0;
      while (ss>>parsedInput){
        char buff[mytitreur.charbyline()];
        if ("-mode"==parsedInput){
          ss>>parsedInput;
          int m;
          if ("alloff"==parsedInput)m=0;
          if ("allon"==parsedInput)m=1;
          if ("turnR"==parsedInput)m=2;
          if ("turnL"==parsedInput)m=3;
          mycarte.setGyro(m,speed,strob);
        }
        if ("-speed"==parsedInput){
          ss>>speed;
        }
        if ("-strob"==parsedInput){
          ss>>strob;
        }
        
      }
    }// end setgyro
    
    if ("setrelais"==parsedInput) {
      while (ss>>parsedInput){
        if ("-on"==parsedInput){
          mycarte.setRelais(1);
        }
        if ("-off"==parsedInput){
          mycarte.setRelais(0);
        }
        
      }
    }// end setgyro
    
    if ("setledtelecook"==parsedInput) {
      while (ss>>parsedInput){
        if ("-on"==parsedInput){
          myteleco.setLedOk(1);
        }
        if ("-off"==parsedInput){
          myteleco.setLedOk(0);
        }
        
      }
    }// end setgyro
    
    if ("setledcarteok"==parsedInput) {
      while (ss>>parsedInput){
        if ("-on"==parsedInput){
          mycarte.setledG(1);
        }
        if ("-off"==parsedInput){
          mycarte.setledG(0);
        }
        
      }
    }// end setgyro
    
    
    if ("DR"==parsedInput) {
      int reg = 0;
      int val = 0;
      int fade = 0;
      while (ss>>parsedInput){
        char buff[mytitreur.charbyline()];
        if ("-reg"==parsedInput){
          ss>>reg;
        }
        if ("-val"==parsedInput){
          ss>>val;
        }
        if ("-fade"==parsedInput){
          ss>>fade;
        }
      }
      fprintf(stderr, "direct acces %u %u %u\n",reg,val,fade);
      mycarte.writeValue(reg,val,fade);
      
    }// end directaccess
    
    if ("testroutine"==parsedInput) {
      int nbr = 1;
      while (ss>>parsedInput){
        char buff[mytitreur.charbyline()];
        if ("-nbr"==parsedInput){
          ss>>nbr;
        }
      }
      fprintf(stderr, "test routine\n");
      testRoutine(nbr);
      
    }// end testroutine
    
  }
  
}


int main (int argc, char * argv[]){
  
signal(SIGTERM, beforekill);
signal(SIGINT, beforekill);
 
  wiringPiSetupGpio();
  pinMode (21, INPUT);


  
cout << "#INITHARDWARE" << endl;
  
  
  while(!init){
    parseInput();
  }
  if(version_py=="-")myteleco.initCarte(1);else myteleco.initCarte(0);
  delay(10);
  if (digitalRead(21)==HIGH) {
    fprintf(stderr, "teleco add at boot\n");
    myteleco.readInterrupt();
    myteleco.start();
    sendStatusTeleco();
  }

  
  wiringPiISR (20, INT_EDGE_RISING, &myInterruptCARTE) ;
  wiringPiISR (21, INT_EDGE_RISING, &myInterruptTELECO) ;

  
  
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

