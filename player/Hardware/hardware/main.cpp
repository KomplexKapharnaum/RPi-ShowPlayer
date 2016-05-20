//
//  main.cpp
//  testc
//
//  Created by SuperPierre on 10/12/2014.
//
//



#include "extSPI.h"

#include <stdio.h>
#include <cstdio>
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
#include "timer.h"
#include "main.h"








//update status on remote, call at load and if status (status, scene, tension... change)
void sendStatusTeleco(){
  float tension = mycarte.checkTension();
  char mess1[17];
  char mess2[17];
  delay(2);
  sprintf(mess1,"git %s",status.c_str());
  sprintf(mess2,"py=%s C=%s",version_py.c_str(),version_c.c_str());
  myteleco.sendString(mess1,mess2,T_MENU_ID_STATUS_GIT_VERSION);
  delay(2);
  sprintf(mess1,"%s",carte_name.c_str());
  sprintf(mess2,"%s %.1fV",carte_ip.c_str(),tension);
  myteleco.sendString(mess1,mess2,T_MENU_ID_STATUS_AUTO_NAME_IP_VOLTAGE);
  delay(2);
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
  mytitreur.text(0,0,buff,msg.length());
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
  mytitreur.text(0,0,buff,msg.length());
}



//parse pyton or bash input from stdin
int parseInput(string input){
  
  if (input=="check_teleco_on_start"){
    //init teleco if already connected // ISSUE HERE
    produce(q,"start_interrupt");
    if (digitalRead(21)==HIGH) {
    produce(q,"interrupt_teleco");
    }
  }

  if(input=="start_interrupt"){
    fprintf(stderr, "main - active interrupt for CARTE et télécomande\n");
    wiringPiISR (20, INT_EDGE_RISING, &myInterruptCARTE);
    wiringPiISR (21, INT_EDGE_RISING, &myInterruptTELECO);
    cout << "#HARDWAREREADY" << endl;
  }

  if (input=="interrupt_teleco") {
    //fprintf(stderr, "main - interrupt from teleco\n");
    if (myteleco.fisrtView()){
      delay(20);
      //fprintf(stderr, "main - delaypass\n");
      //if (digitalRead(21)==LOW) return 2;
      //fprintf(stderr, "main - reel interrupt\n");
    }
    if (digitalRead(21)==LOW) return 2;
    delay(1);
    if (digitalRead(21)==LOW) return 2;
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
      delay(2);
      for (int i=T_MENU_ID_STATUS_SCENE; i<T_MENU_ID_LOG_0; i++) {
        char mess1[17];
        char mess2[17];
        strncpy(mess1, popup[i][0].c_str(), sizeof(mess1));
        strncpy(mess2, popup[i][1].c_str(), sizeof(mess2));
        myteleco.sendString(mess1,mess2,i);
        delay(2);
      }
      delay(2);
      myteleco.start();
    }

    return 0;
  }
  
  if (input=="interrupt_carte") {
    //fprintf(stderr, "main - interrupt from carte\n");
    if (digitalRead(20)==LOW) return 2;
    delay(1);
    if (digitalRead(20)==LOW) return 2;
    mycarte.readInterrupt();
    if(mycarte.needStatusUpdate) sendStatusTeleco();
    return 0;
  }
  
  if (input=="initcarte_local") {
    fprintf(stderr, "main - init teleco with local poweroff\n");
    myteleco.initCarte(1);
    produce(q,"check_teleco_on_start");
    delay(10);
    return 0;
  }
  
  if (input=="initcarte_main") {
    fprintf(stderr, "main - init teleco with main program poweroff\n");
    myteleco.initCarte(0);
    produce(q,"check_teleco_on_start");
    delay(10);

    return 0;
  }
  
  if (input=="kill") {
    //turn off light
    mycarte.setRelais(0);
    //turn off titreur
    mytitreur.allLedOff();
    mytitreur.powerdown();
    //update status
    status="noC";
    //power off hardware
    mycarte.writeValue(POWERDOWN,100);
    delay(50);
    //power off remote
    myteleco.reset();
    //myteleco.readOrSetTelecoLock(T_POWEROFF);
    //exit program
    fprintf(stderr, "\x1b[32mbye bye\n\x1b[0m");
    live=false;
    delay(10);
  }
  
  if (input=="start_timer_for_titreur") {
    timertitreur=true;
    t.create(0, 20,
             []() {
               //produce(q, "update_titreur");
               mytitreur.updateText();
             });
    return 0;
  }
  
  if (input=="update_titreur") {
    mytitreur.updateText();
    return 0;
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
        if ("-manualmode"==parsedInput){
          ss>>manualLightMode;
          mycarte.setManualLightMode(manualLightMode);
        }
      }
      init=1;
      
      mytitreur.allLedOff();
      mytitreur.twolineText(carte_name,carte_ip,NO_SCROLL_NORMAL);
      produce(q,"initcarte_main");
    }else{
      fprintf(stderr, "main - error you must init first\ninitconfig -titreurNbr [int] -carteVolt [int] -name [string] -ip [string]\n");
    }
    if ("DEBUG"==parsedInput) {
      //get false init for debug purpose
      fprintf(stderr, "main - overpass standard debug init\n");
      mytitreur.initTitreur(6,MODULE_24x16);
      mycarte.initCarte(PWM_LEDB,LIPO12);
      carte_name="TEST STAND";
      carte_ip="2.0.2.XXX";
      init=1;
      mycarte.setManualLightMode(0);
      //mytitreur.putChar(0,0,'S');
      produce(q,"initcarte_local");
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
      string line1="";
      string line2="";
      int speed = 250;
      int type = NO_SCROLL_NORMAL;
      while (ss>>parsedInput){
        if ("-line1"==parsedInput){
          ss>>line1;
          replace( line1.begin(), line1.end(), '_', ' ');
        }
        if ("-line2"==parsedInput){
          ss>>line2;
          replace( line2.begin(), line2.end(), '_', ' ');
        }
        if ("-allon"==parsedInput){
          mytitreur.allLedOn();
          return 0;
        }
        if ("-alloff"==parsedInput){
          mytitreur.allLedOff();
          return 0;
        }
        if ("-speed"==parsedInput){
          ss>>speed;
        }
        if ("-type"==parsedInput){
          ss>>parsedInput;
          
          if ("SCROLL_NORMAL"==parsedInput || "SN"==parsedInput || "sn"==parsedInput) {
            type=SCROLL_NORMAL;
          }
          if ("SCROLL_LOOP_NORMAL"==parsedInput || "SLN"==parsedInput || "sln"==parsedInput) {
            type=SCROLL_LOOP_NORMAL;
          }
          if ("SCROLL_VERTICAL_NORMAL"==parsedInput) {
            type=SCROLL_VERTICAL_NORMAL;
          }
          if ("SCROLL_VERTICAL_LOOP_NORMAL"==parsedInput) {
            type=SCROLL_VERTICAL_LOOP_NORMAL;
          }
          if ("NO_SCROLL_BIG"==parsedInput || "B"==parsedInput || "b"==parsedInput) {
            type=NO_SCROLL_BIG;
          }
          if ("SCROLL_BIG"==parsedInput || "SB"==parsedInput || "sb"==parsedInput) {
            type=SCROLL_BIG;
          }
          if ("SCROLL_LOOP_BIG"==parsedInput || "SLB"==parsedInput || "slb"==parsedInput) {
            type=SCROLL_LOOP_BIG;
          }
          if ("SCROLL_VERTICAL_BIG"==parsedInput) {
            type=SCROLL_VERTICAL_BIG;
          }
          if ("SCROLL_VERTICAL_LOOP_BIG"==parsedInput) {
            type=SCROLL_VERTICAL_LOOP_BIG;
          }
        }
      }
      mytitreur.twolineText(line1,line2,type,speed);
      //produce(q,"update_titreur");
      if(!timertitreur)produce(q,"start_timer_for_titreur");
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
    
    if ("DR"==parsedInput) {
      //direct access of carte register for debug
      int reg = 0;
      int val = -1;
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
      if (val==-1){
        val = mycarte.readValue(reg);
        fprintf(stderr, "main - direct read acces %u = %u\n",reg,val);
      }else {
        fprintf(stderr, "main - direct acces %u = %u f%u\n",reg,val,fade);
        mycarte.writeValue(reg,val,fade);
      }
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
    //if(!(message=="interrupt_carte" || message=="interrupt_teleco"|| message=="update_titreur"))
    fprintf(stderr, "main - prog push %s\n",message.c_str());
    q.push(message);
}

void produce_first(Queue<string>& q, string message) {
    //if(!(message=="interrupt_carte" || message=="interrupt_teleco"|| message=="update_titreur"))
    fprintf(stderr, "main - prog push_first %s\n",message.c_str());
    q.push_first(message);
}


void readcin(Queue<string>& q) {
  string input;
  while (live) {
    getline(cin, input);
    if(input.length()>3){
        fprintf(stderr, "main - cin push %s\n",input.c_str());
        q.push(input);
    }
  }
}

void consume(Queue<string>& q) {
  bool loop_continue = true;
  while (loop_continue) {
    auto item = q.pop();
    //if(!(item=="interrupt_carte" || item=="interrupt_teleco" || item=="update_titreur"))
    fprintf(stderr, "main - popped %s\n",item.c_str());
    parseInput(item);
    if (item=="kill"){
        loop_continue=false;
        delay(100);
    }
  }
}

//one listener to cin
//thread reader(bind(readcin, ref(q)));

//one reader, execute order one by one
thread consumer(bind(&consume, ref(q)));

  
void killthread() {
  produce(q,"kill");
  consumer.join();
  //reader.join(); TODO: find way to kill reader before exit
}

//clean befor exit
void beforekill(int signum)
{
  killthread();
  //consumer.join();
  exit(signum);
}


//catch interrupt from carte
void myInterruptCARTE (void) {
  produce_first(q,"interrupt_carte");
}


//catch interrupt from remote
void myInterruptTELECO(void) {
  produce_first(q,"interrupt_teleco");
}


int main (int argc, char * argv[]){
  
  //catch exit signal
  signal(SIGTERM, beforekill);
  signal(SIGINT, beforekill);
  
  wiringPiSetupGpio();
  pinMode (21, INPUT);
  pinMode (20, INPUT);

  cout << "#INITHARDWARE" << endl;




  readcin(q);
  //program start

  consumer.join();

  exit(0);
  
  return 0;
  
}


