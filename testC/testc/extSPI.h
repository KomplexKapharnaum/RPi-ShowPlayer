//
//  extSPI.h
//  testc
//
//  Created by SuperPierre on 10/12/2014.
//
//


/*example of use :
 
 SIMPLE :
 
 extSPI mySPI;                      declare your object
 mySPI.initSPI(21,1000000);         init simple mode GPIOselect21 speed 1MHz
 return mySPI.send(0xA3);           send one byte 0xA3
 
 VIA HC595 :
 
 extSPI mySPI;                      declare your object
 mySPI.initSPIHC595(2,21,1000000);  init HC595 mode 2 chip, rck GPIO 21, speed
 mySPI.selectHC595csline(5);        select cs line you want
 unsigned char buff[10];            build tab of byte
 for (int i=0; i<10; i++) {
 buff[i]=i;
 }
 return mySPI.send(buff,10);        send
 
 */
 


#ifndef __testc__extSPI__
#define __testc__extSPI__




class extSPI{

private:
  int init;
  int spiWRMode;
  int spiRDMode;
  int spiBitsPerWord;
  int spiSpeed;
  int cs;
  int rck;
  int nbmodule;
  int classmode;
  int selectedCSofHC595;
  
  void commonInit(int _spiSpeed);
  void HC595select();
  void HC595unselect();
  int check();
  

public:
  extSPI();
  void initSPI(int csGPIOpin,int _spiSpeed);
  void initSPIHC595(int _nbHC595, int rckGPIOpin, int _spiSpeed);
  void selectHC595csline(int _selectedCSofHC595);
  //cs from 0 coresponding in the first out from hc595 daisy chain
  int send(unsigned char _byte);
  int send(unsigned char *_tab,int _len);
  
  
};



#endif /* defined(__testc__extSPI__) */
