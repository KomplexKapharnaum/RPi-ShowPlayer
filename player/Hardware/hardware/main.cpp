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

#include "Queue.h"



using namespace std; //for native use of string

bool live=true;

//string to hold data from pyton program
string carte_name;
string carte_ip;
string scene="-";
string version_py="-";
string version_c="1.1";
string status="-";
string voltage="-";
string buttonline="OK   B   A";
string popup[11][2];
int init=0;

//safe queue to put message in
Queue<string> q;


//C object of hardware
Carte mycarte;
Teleco myteleco;
Titreur mytitreur;


//update status on remote, call at load and if status (status, scene, tension... change)
void sendStatusTeleco(){
  float tension = mycarte.checkTension();
  char mess1[17];
  char mess2[17];
  delay(10);
  sprintf(mess1,"git %s",status.c_str());
  sprintf(mess2,"py=%s C=%s",version_py.c_str(),version_c.c_str());
  myteleco.sendString(mess1,mess2,T_MENU_ID_STATUS_GIT_VERSION);
  delay(10);
  sprintf(mess1,"%s",carte_name.c_str());
  sprintf(mess2,"%s %.1fV",carte_ip.c_str(),tension);
  myteleco.sendString(mess1,mess2,T_MENU_ID_STATUS_AUTO_NAME_IP_VOLTAGE);
  delay(10);
  sprintf(mess1,"%.1fV %s",tension,scene.c_str());
  sprintf(mess2,"%s",buttonline.c_str());
  myteleco.sendString(mess1,mess2,T_MENU_ID_SHOW_STATUS);
}



//test output light, titreur
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



//parse pyton or bash input from stdin
int parseInput(string input){
  if (input=="interrupt_teleco") {
    //fprintf(stderr, "main - interrupt from teleco\n");
    if (myteleco.fisrtView()){
      delay(20);
      //fprintf(stderr, "main - delaypass\n");
      if (digitalRead(21)==LOW) return 2;
      //fprintf(stderr, "main - reel interrupt\n");
    }
    
    myteleco.readInterrupt();
    if(myteleco.needtestroutine){
      fprintf(stderr, "main - teleco need test routine\n");
      myteleco.needtestroutine=0;
      testRoutine(1);
    }
    if(myteleco.needstart){
      fprintf(stderr, "main - teleco need start\n");
      myteleco.needstart=0;
      sendStatusTeleco();
      delay(20);
      for (int i=T_MENU_ID_STATUS_SCENE; i<T_MENU_ID_LOG_0; i++) {
        char mess1[17];
        char mess2[17];
        strncpy(mess1, popup[i][0].c_str(), sizeof(mess1));
        strncpy(mess2, popup[i][1].c_str(), sizeof(mess2));
        myteleco.sendString(mess1,mess2,i);
        delay(10);
      }
      delay(20);
      myteleco.start();
    }
    return 0;
  }
  
  if (input=="interrupt_carte") {
    //fprintf(stderr, "main - interrupt from carte\n");
    mycarte.readInterrupt();
    if(mycarte.needStatusUpdate) sendStatusTeleco();
    return 0;
  }
  
  if (input=="initcarte_local") {
    fprintf(stderr, "main - init teleco with local poweroff\n");
    myteleco.initCarte(1);
    delay(10);
    return 0;
  }
  
  if (input=="initcarte_main") {
    fprintf(stderr, "main - init teleco with main program poweroff\n");
    myteleco.initCarte(0);
    delay(10);
    return 0;
  }
  
  if (input=="kill") {
    //turn off light
    mycarte.setGyro(0,200);
    mycarte.led10WValue(0);
    mycarte.rgbValue(0,0,0);
    mycarte.setRelais(0);
    //turn off titreur
    mytitreur.allLedOff();
    mytitreur.powerdown();
    //update status
    status="noC";
    delay(5);
    //power off hardware
    mycarte.writeValue(POWERDOWN,100);
    //power off remote
    myteleco.reset();
    //myteleco.readOrSetTelecoLock(T_POWEROFF);
    //exit program
    fprintf(stderr, "\x1b[32mbye bye\n\x1b[0m");
    delay(10);
  }
  
  //other message from main program or stdin
  fprintf(stderr, "\n\x1b[33mGETCOMMAND : %s\n\x1b[0m",input.c_str());
  stringstream ss(input);
  string parsedInput;
  ss>>parsedInput;
  if (init==0){
    //first call, init not set
    if ("initconfig"==parsedInput) {
      //get init config
      while (ss>>parsedInput){
        if ("-titreurNbr"==parsedInput){
          int nbmodule;
          ss>>nbmodule;
          mytitreur.initTitreur(nbmodule,MODULE_24x16);
        }
        if ("-carteVolt"==parsedInput){
          ss>>parsedInput;
          voltage=parsedInput;
          if(voltage=="life12")mycarte.initCarte(PWM_LEDB,LIFE12);
          else if(voltage=="lipo12")mycarte.initCarte(PWM_LEDB,LIPO12);
          else if(voltage=="pb12")mycarte.initCarte(PWM_LEDB,PB12);
          else if(voltage=="lipo24")mycarte.initCarte(PWM_LEDB,LIPO24);
          else if(voltage=="life24")mycarte.initCarte(PWM_LEDB,LIFE24);
          else if(voltage=="pb24")mycarte.initCarte(PWM_LEDB,PB24);
          else mycarte.initCarte(PWM_LEDB,VOLTAGENONE);
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
      fprintf(stderr, "main - error you must init first\ninitconfig -titreurNbr [int] -carteVolt [int] -name [string] -ip [string]\n");
    }
    if ("S"==parsedInput) {
      //get false init for debug purpose
      fprintf(stderr, "main - overpass standard debug init\n");
      mytitreur.initTitreur(6,MODULE_24x16);
      mycarte.initCarte(PWM_LEDB,LIPO12);
      carte_name="TEST STAND";
      carte_ip="2.0.2.XXX";
      init=1;
      mytitreur.putChar(0,0,'S');
    }
    
  }else{
    //init passed, parse others
    if ("info"==parsedInput) {
      //change status
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
      //send data to the remote
      char mess1[17];
      char mess2[17];
      int type=0;
      while (ss>>parsedInput){
        if ("-type"==parsedInput){
          ss>>parsedInput;
          if (parsedInput=="log") type = T_MENU_ID_LOG_0;
          if (parsedInput=="scenario") type = T_MENU_ID_STATUS_SCENE;
          if (parsedInput=="usb") type = T_MENU_ID_STATUS_USB;
          if (parsedInput=="media") type = T_MENU_ID_STATUS_MEDIA;
          if (parsedInput=="sync") type = T_MENU_ID_STATUS_SYNC;
          if (parsedInput=="user") type = T_MENU_ID_STATUS_USER;
          if (parsedInput=="error") type = T_MENU_ID_STATUS_ERROR;
          popup[type][0]="                ";
          popup[type][1]="                ";
        }
        if ("-line1"==parsedInput){
          ss>>parsedInput;
          replace( parsedInput.begin(), parsedInput.end(), '_', ' ');
          popup[type][0]=parsedInput;
        }
        if ("-line2"==parsedInput){
          ss>>parsedInput;
          replace( parsedInput.begin(), parsedInput.end(), '_', ' ');
          popup[type][1]=parsedInput;
          if (type==T_MENU_ID_STATUS_SCENE) {
            scene=parsedInput;
            sendStatusTeleco();
          }
        }
      }
      strncpy(mess1, popup[type][0].c_str(), sizeof(mess1));
      strncpy(mess2, popup[type][1].c_str(), sizeof(mess2));
      if(type!=0)myteleco.sendString(mess1,mess2,type);
    }
    
    
    
    if ("initconfig"==parsedInput) {
      fprintf(stderr, "main - error already init\n");
    }
    
    if ("texttitreur"==parsedInput) {
      //write on titreur
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
    }
    
    if ("setlight"==parsedInput) {
      //change light
      int fade=0;
      int strob=0;
      while (ss>>parsedInput){
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
      //change gyro flex led
      int speed=350;
      int strob=0;
      while (ss>>parsedInput){
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
      //change onboard relais state
      while (ss>>parsedInput){
        if ("-on"==parsedInput){
          mycarte.setRelais(1);
        }
        if ("-off"==parsedInput){
          mycarte.setRelais(0);
        }
        
      }
    }
    
    if ("setledtelecook"==parsedInput) {
      //green led under ok push on remote
      while (ss>>parsedInput){
        if ("-on"==parsedInput){
          myteleco.setLedOk(1);
        }
        if ("-off"==parsedInput){
          myteleco.setLedOk(0);
        }
        
      }
    }
    
    if ("setledcarteok"==parsedInput) {
      //green led under right of carte
      while (ss>>parsedInput){
        if ("-on"==parsedInput){
          mycarte.setledG(1);
        }
        if ("-off"==parsedInput){
          mycarte.setledG(0);
        }
        
      }
    }
    
    if ("settelecolock"==parsedInput) {
      //set lock status on remote
      while (ss>>parsedInput){
        if ("-lock"==parsedInput){
          myteleco.readOrSetTelecoLock(T_ISLOCK);
        }
        if ("-unlock"==parsedInput){
          myteleco.readOrSetTelecoLock(T_ISOPEN);
        }
        if ("-sleep"==parsedInput){
          myteleco.readOrSetTelecoLock(T_ISLOCKWITHSLEEP);
        }
        if ("-powerdown"==parsedInput){
          myteleco.readOrSetTelecoLock(T_POWEROFF);
        }
        if ("-read"==parsedInput){
          int state = myteleco.readOrSetTelecoLock();
          cout << "#TELECO_LOCK_STATE "<< state << endl;
        }
      }
    }
    
    if ("powerdownhardware"==parsedInput) {
      //exit c main programm for debug
      //beforekill(0);
      live=false;
    }
    
    
    if ("DR"==parsedInput) {
      //direct access of carte register for debug
      int reg = 0;
      int val = 0;
      int fade = 0;
      while (ss>>parsedInput){
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
      fprintf(stderr, "main - direct acces %u %u %u\n",reg,val,fade);
      mycarte.writeValue(reg,val,fade);
      
    }// end directaccess
    
    if ("testroutine"==parsedInput) {
      //start testroutine
      int nbr = 1;
      while (ss>>parsedInput){
        if ("-nbr"==parsedInput){
          ss>>nbr;
        }
      }
      fprintf(stderr, "main - test routine\n");
      testRoutine(nbr);
      
    }// end testroutine
    
  }
  return 1;
}

void produce(Queue<string>& q, string message) {
  fprintf(stderr, "main - push %s\n",message.c_str());
  q.push(message);
}

void consume(Queue<string>& q) {
  bool loop_continue = true;
  while (loop_continue) {
    auto item = q.pop();
    fprintf(stderr, "main - popped %s\n",item.c_str());
    if (item=="kill")loop_continue=false;
    parseInput(item);
  }
}


  
//one reader, execute order one by one
thread consumer(bind(&consume, ref(q)));
  
void killthread() {
  produce(q,"kill");
  consumer.join();
}

//clean befor exit
void beforekill(int signum)
{
  killthread();
  exit(signum);
}


//catch interrupt from carte
void myInterruptCARTE (void) {
  produce(q,"interrupt_carte");
}


//catch interrupt from remote
void myInterruptTELECO(void) {
  produce(q,"interrupt_teleco");
}


int main (int argc, char * argv[]){
  

  
  //catch exit signal
  signal(SIGTERM, beforekill);
  signal(SIGINT, beforekill);
  
  wiringPiSetupGpio();
  pinMode (21, INPUT);
  
  //program start
  cout << "#INITHARDWARE" << endl;

  
  //wait for init
  string input;
  do {
    getline(cin, input);
    produce(q,input);
  }while(!init);
  
  //init carte
  if(version_py=="-") {
    produce(q,"initcarte_local");
  }
  else {
    produce(q,"initcarte_main");
  }
  
  //init teleco if already connected // ISSUE HERE
  if (digitalRead(21)==HIGH) {
    produce(q,"interrupt_teleco");
  }
  
  //start interrupt thread
  fprintf(stderr, "main - active interrupt for CARTE et télécomande\n");
  wiringPiISR (20, INT_EDGE_RISING, &myInterruptCARTE) ;
  wiringPiISR (21, INT_EDGE_RISING, &myInterruptTELECO) ;
  
  
  //wait for input
  do {
    getline(cin, input);
    produce(q,input);
  }while(live);
  
  killthread();
  return 0;
  
}


