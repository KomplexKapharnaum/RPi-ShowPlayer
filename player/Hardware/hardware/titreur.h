//
//  titreur.h
//  testc
//
//  Created by SuperPierre on 20/02/2015.
//
//

#ifndef __testc__titreur__
#define __testc__titreur__

#include <iostream>
#include "extSPI.h"

#define MODULE_24x16 48 //nombre de char dans la matrice
#define MODULE_32x8 32

class Titreur{
  
private:
  void ht1632_sendcmd (int chipNo, unsigned char command);
  unsigned char *matrix;
  unsigned char *output;
  int typeModule;
  int cleanCharArray(char Str1[]);
  int messageLength;
  std::string debug;
  
protected:
  int nb_module;
  int SPIspeed;
  void initModule(int m);
  extSPI mySPI;
  unsigned int buffer;
  void flushMatrix();
  
  
  
  public :
  void text(int x, int y,char Str1[]);
  void putChar(int x, int y, char c);
  void initTitreur(int _nb_module, int _typeModule);
  void testScreen();
  void plot(int x,int y,int val);
  void printScreen();
  void allLedOn();
  void allLedOff();
  int charbyline();
  ~Titreur();
  
};

#endif /* defined(__testc__titreur__) */