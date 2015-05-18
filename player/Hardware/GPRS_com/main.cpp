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

using namespace std;

void readRX(int fd,int end){
  //----- CHECK FOR ANY RX BYTES -----
  if (fd != -1)
  {
    string input = "";
    cout <<  "read" << endl;
    
    while(1){
      while(!serialDataAvail(fd));
      int t = serialGetchar (fd);
      input+=t;
      //cout << (char)t;


      if(t==end){

        stringstream ss(input);
        while(getline(ss,input,'\n')){
            if(input.length()>3){
                cout << endl << "line " << input << endl;
                istringstream iss(input);
                string word="";
                iss>>word;
                if(word=="+CMT:"){
                    cout << "new sms" << endl;
                    iss >> word;
                    stringstream ss(word);
                    getline(ss,word,'"');
                    cout << 1 << word;
                    getline(ss,word,'"');
                    cout << 2 << word;

                }
            }
        }

        break;
        
      }
      
    }
    
  }
  
}



int main (int argc, char * argv[]){
  
  int uart0_filestream = -1;

  //serial RX coté RPI tx coté modem pin du haut sur la carte, pin 7 modem
  //serial TX coté RPI rx coté modem pin du bas sur la carte, pin 8 modem
  cout <<  "start gsm reader" << endl;
  uart0_filestream = serialOpen ("/dev/ttyAMA0", 19200);
  //serialPrintf (uart0_filestream, "AT+CMGR=1\r\n") ;
  /*delay(5);
  //check sim comm
  serialPrintf (uart0_filestream, "ATI\r\n");
  readRX(uart0_filestream,(int)'K');
  //
  delay(50);*/

  
  
  bool live=true;
  while(live){
    readRX(uart0_filestream,(int)'K');

  }
  
  serialClose(uart0_filestream);

  return 0;
  
}




