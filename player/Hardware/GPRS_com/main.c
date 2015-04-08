//
//  main.c
//  GPRS_com
//
//  Created by SuperPierre on 21/01/2015.
//
//

#include <stdio.h>
#include <string.h>

#include <wiringSerial.h>

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
      
      printf("%c",(char)t);
      if(t==end){
        break;
        
      }
      
    }
    
  }
  
}



int main (int argc, char * argv[]){
  
  int uart0_filestream = -1;
  
  
  char dest[5][13];
  strcpy(dest[0], "+33678517297");
  strcpy(dest[1], "+33635318343");
  strcpy(dest[2], "+33603435161");
  strcpy(dest[3], "+33681961963");
  strcpy(dest[4], "+33618017372");
  
  uart0_filestream = serialOpen ("/dev/ttyAMA0", 19200);
  //serialPrintf (uart0_filestream, "AT+CMGR=1\r\n") ;
  
  serialPrintf (uart0_filestream, "AT+CMGF=1\r") ;
  printf("OUT AT+CMGF=1\n");
  //while(!serialDataAvail(uart0_filestream));
  readRX(uart0_filestream,(int)'K');
  serialPrintf (uart0_filestream, "AT+CMGD=4\r") ;
  printf("OUT AT+CMGD=4\n");
  //while(!serialDataAvail(uart0_filestream));
  readRX(uart0_filestream,(int)'K');
  delay(50);
  
  
  
  int i=0;
  int j=0;
  for (j=0; j<10; j++) {
    for (i=0; i<5; i++) {
      serialPrintf (uart0_filestream, "AT+CMGS=\"%s\"\r",dest[i]) ;
      printf("OUT AT+CMGS=\"%s\"\n",dest[i]);
      //while(!serialDataAvail(uart0_filestream));
      readRX(uart0_filestream,(int)'>');
      serialPrintf (uart0_filestream, "Les temps sont durs, il faut se serrer la ceinture. Il fait froid, le froid de l'hiver. Les sms ne sont pas rapides, c'est pas facile. %i\r",j);
      printf("OUT Salut%i\r\n",j);
      //while(!serialDataAvail(uart0_filestream));
      readRX(uart0_filestream,10);
      serialPutchar (uart0_filestream, (char)26) ;
      printf("OUT ‰c\n",(char)26);
      delay(5);
      serialPrintf (uart0_filestream, "\r") ;
      printf("OUT \r\n");
      //while(!serialDataAvail(uart0_filestream));
      readRX(uart0_filestream,(int)'K');
      delay(50);
    
    }
    
    
    
    
  }
  
  
  
  //printf("bisous\n");
  
  
  serialClose(uart0_filestream);
  
  // Don't forget to clean up
  //close(uart0_filestream);
  return 0;
  
}




