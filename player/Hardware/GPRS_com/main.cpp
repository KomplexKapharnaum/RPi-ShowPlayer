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
    printf("IN %i : ",end);
    int count =0;
    int rx_buffer[256];
    //printf("\nnew read\n");
    
    while(1){
      while(!serialDataAvail(fd));
      /*
       // Read up to 255 characters from the port if they are there
       unsigned char rx_buffer[256];
       int rx_length = read(fd, (void*)rx_buffer, 255);		//Filestream, buffer to store in, number of bytes to read (max)
       if (rx_length < 0)
       {
       //An error occured (will occur if there are no bytes)
       printf("pb");
       break;
       }
       else if (rx_length == 0)
       {
       printf("no data");
       //No data waiting
       break;
       }
       else
       {
       //Bytes received
       rx_buffer[rx_length] = '\0';
       printf("%i bytes read : %s\n", rx_length, rx_buffer);
       }
       }
       */
      int t = serialGetchar (fd);

      cout <<  (char)t;
      if(t==end){
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
  delay(5);
  //check sim comm
  serialPrintf (uart0_filestream, "ATI\r\n");
  readRX(uart0_filestream,(int)'K');
  //
  delay(50);
  cout <<  "read" << endl;
  
  
  bool live=true;
  while(live){
    readRX(uart0_filestream,(int)'K');
  }
  
  serialClose(uart0_filestream);

  return 0;
  
}




