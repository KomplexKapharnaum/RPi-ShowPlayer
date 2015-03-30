//
//  extSPI.h
//  testc
//
//  Created by SuperPierre on 10/12/2014.
//
//

#ifndef __testc__extSPI__
#define __testc__extSPI__

class extSPI{

private:
  int spiWRMode;
  int spiRDMode;
  int spiBitsPerWord;
  int spiSpeed;
  int errFlag;
  int cs;
  int nbmodule;
  
  

public:
  
  extSPI(int _cs=0,int _spiSpeed=1000000);
  int send(unsigned char _byte);
  
};

class extSPIwithHCT595{
private:
  extSPI mySPI;
  int nbmodule;
  int spiSpeed;
  int mosi;
  int sclk;
  
  int rck;
  void select(int cs);
  void unselect();
  
public:
  extSPIwithHCT595(int _nbmodule, int _rck, int _spiSpeed=1000000);
  int send(unsigned char _byte, int cs);
  
};


#endif /* defined(__testc__extSPI__) */
