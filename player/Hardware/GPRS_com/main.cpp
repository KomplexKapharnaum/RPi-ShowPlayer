#include <stdio.h>
#include <string.h>
#include <wiringSerial.h>
#include <wiringPi.h>
#include <wiringPiSPI.h>

#include <iostream>
#include <fstream>
#include <cstring>
#include <sstream>
#include <string>
#include <algorithm>

#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <fstream>

#include <time.h>
#include <sys/time.h>
#include <stdint.h>
#include <signal.h>

#include "main.h"

unsigned long long mstime() {
	struct timeval tv;
  
	gettimeofday(&tv, NULL);
  
	unsigned long long millisecondsSinceEpoch =
  (unsigned long long)(tv.tv_sec) * 1000 +
  (unsigned long long)(tv.tv_usec) / 1000;
  
	return millisecondsSinceEpoch;
}


using namespace std;

int uart0_filestream = -1;
ofstream outfilenum;
ofstream outfiletext;

string programName = " gsm - ";
unsigned long long waitingdelay = 100;

string lastnum="";
bool waitingsms = false;
string smsText = "";

#include <lo/lo.h>
#include <lo/lo_cpp.h>

#define SENDOSC true

lo::Address ph("2.0.2.100", "1783");
lo::Address regie("2.0.0.79", "2222");
lo::Address regiebis("2.0.0.100", "2222");

void api(){
  cout << mstime() << programName;
}


void sendOsc(){
  if (waitingsms){
    if (lastnum!="") {
      api();
      cout << "osc send sms text = " << smsText <<  endl;
      lo::Message m;
      m.add_string(smsText);
      regie.send("/smsFL",m);
      regiebis.send("/smsFL",m);
      m.add_string(lastnum);
      ph.send("/monitor_sms",m);
      outfiletext << lastnum << endl<< smsText << endl << endl;
      smsText="";
      lastnum="";
      waitingsms=false;
    }
  }
}

void readRX(int fd){
  //----- CHECK FOR ANY RX BYTES -----
  if (fd != -1)
  {
    string input = "";
    unsigned long long startReceive = mstime();
    api();
    cout << "read" << endl;
    bool live = true;
    while(live){
      while(!serialDataAvail(fd)){
        usleep(10000);
        if (startReceive + waitingdelay < mstime()) {
          sendOsc();
        }
      }
      int t = serialGetchar (fd);
      //char r;
      /*if (t & 0x80) {
         r = t;
      } else {
        r = (char) (0xc0 | (unsigned) t >> 6);
        r = (char) (0x80 | (t & 0x3f));
      }*/
        
      
      if(t<128 && t>0) {
        input+=t;
      }else {
        if(t>128){
        input+=195;
        input+=t-64;
        }
      }
      //cout <<"/"<<t<<(char)t;
      
      
      if(t=='\n'){
        
        stringstream ss(input);
        while(getline(ss,input,'\n')){
          
          if(input.length()>1){
            api();
            cout << "serial line " << input << endl;
            istringstream iss(input);
            string word="";
            iss>>word;
            if(word=="+CMT:"){
              sendOsc();
              iss >> word;
              stringstream ss(word);
              getline(ss,word,'"');
              getline(ss,word,'"');
              api();
              cout << "sms num = " << word << endl;
              lastnum = word;
              outfilenum << word << endl;
              startReceive = mstime();
              
            }else {
              if (lastnum!="") {
                if (!waitingsms) {
                  smsText.append(input);
                  smsText.append("\n");
                  waitingsms = true;
                } else {
                  smsText.append(input);
                  smsText.append(" ");
                }
              }
            }
          }
        }
        
      }
    }
    
  }
  
}





//clean befor exit
void beforekill(int signum)
{
  serialClose(uart0_filestream);
  api();
  cout <<  "end prog" << endl;
  exit(signum);
}


int main (int argc, char * argv[]){
  
  signal(SIGTERM, beforekill);
  signal(SIGINT, beforekill);
  
  
  outfilenum.open("/dnc/media/sms/dest.txt", std::ios_base::app);
  outfiletext.open("/dnc/media/sms/sms.txt", std::ios_base::app);
  
  //serial RX coté RPI tx coté modem pin du haut sur la carte, pin 7 modem
  //serial TX coté RPI rx coté modem pin du bas sur la carte, pin 8 modem
  api();
  cout <<  "start gsm reader regie 2.0.0.79 ou 100" << endl;
  uart0_filestream = serialOpen ("/dev/ttyAMA0", 19200);
  //serialPrintf (uart0_filestream, "AT+CMGR=1\r\n") ;
  /*delay(5);
   //check sim comm
   serialPrintf (uart0_filestream, "ATI\r\n");
   readRX(uart0_filestream,(int)'K');
   //
   delay(50);*/
  
  
  if(SENDOSC){
    api();
    cout <<  "send osc mode é" << endl;
    ph.send("/monitor_sms", "s", "start service é");
  }
  
  //looping function
  readRX(uart0_filestream);
  
  serialClose(uart0_filestream);
  api();
  cout <<  "end prog" << endl;
  
  return 0;
  
}




