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
#include <cstring>
#include <string>
#include <algorithm>

#define MODULE_24x16 48 //nombre de char dans la matrice
#define MODULE_32x8 32

#define NO_SCROLL_NORMAL 0
#define SCROLL_NORMAL 1
#define SCROLL_LOOP_NORMAL 2
#define SCROLL_VERTICAL_NORMAL 11
#define SCROLL_VERTICAL_LOOP_NORMAL 12
#define NO_SCROLL_BIG 100
#define SCROLL_BIG 101
#define SCROLL_LOOP_BIG 102
#define SCROLL_VERTICAL_BIG 111
#define SCROLL_VERTICAL_LOOP_BIG 112


class Titreur{
  
private:
  void ht1632_sendcmd (int chipNo, unsigned char command);
  unsigned char *matrix;
  unsigned char *output;
  int typeModule;
  int cleanCharArray(char Str1[]);
  int type;
  std::string line1, line2;
  int needUpdate;
  unsigned long long lastRefresh;
  int scrollSpeed;
  int xpos,ypos;
  int delaytime;
  int big;
  

  
protected:
  int nb_module;
  int SPIspeed;
  void initModule(int m);
  extSPI mySPI;
  unsigned int buffer;
  void flushMatrix();
  int charbyline();
  int pixelbyline();
  int pixelHeight();
  
  
public :
  void text(int x, int y,char Str1[], int messageLength);
  void putChar(int x, int y, char c);
  void initTitreur(int _nb_module, int _typeModule);
  void testScreen();
  void plot(int x,int y,int val);
  void printScreen();
  void allLedOn();
  void allLedOff();
  void powerdown();
  void twolineText(std::string _line1,std::string _line2,int _type, int _speed=250);
  void updateText();
  ~Titreur();

  
};

#endif /* defined(__testc__titreur__) */