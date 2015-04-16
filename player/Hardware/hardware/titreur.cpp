//
//  titreur.cpp
//  testc
//
//  Created by SuperPierre on 20/02/2015.
//
//

#include <cstdlib>

#include "titreur.h"
#include "extSPI.h"

#include <stdio.h>
#include <fcntl.h>
#include <errno.h>

#include <wiringPi.h>
#include <wiringPiSPI.h>

#include "ht1632.h"
#include "font2.h"

#include <string>
#include <string.h>

std::string debug="titreur - ";


void Titreur::initTitreur(int _nb_module, int _typeModule){
  nb_module=_nb_module;
  typeModule=_typeModule;
  SPIspeed=1000000;
  mySPI.initSPI();
  int patch[8] = {3, 1, 0, 2, 6, 7, 4, 5};
  
  for (int i=0; i<nb_module; i++) {
    mySPI.addChipSelectWithHC595Buffer(17,patch[i],SPIspeed);
    initModule(i);
  }
  matrix = (unsigned char *) malloc(typeModule*nb_module+1);
  output = (unsigned char *) malloc(typeModule+4);
  
  
  for (int i=0; i<typeModule*nb_module; i++) {
    *(matrix+i)=0;
  }
}



//problem, plutôt faire des commandes écrites pour être directement envoyée en SPI.

void Titreur::initModule(int m){
  fprintf(stderr, "%sinit titreur module %u\n",debug.c_str(),m);
  //mySPI.setkeepSelect();
  
  ht1632_sendcmd(m, HT1632_CMD_SYSDIS);  // Disable system
  //selectMappingType(m);
  ht1632_sendcmd(m, HT1632_CMD_MSTMD); 	/* Master Mode */
  ht1632_sendcmd(m, HT1632_CMD_RCCLK);  // HT1632C
  ht1632_sendcmd(m, HT1632_CMD_SYSON); 	/* System on */
  if (typeModule==MODULE_24x16) ht1632_sendcmd(m, HT1632_CMD_COMS01);
  if (typeModule==MODULE_32x8) ht1632_sendcmd(m, HT1632_CMD_COMS00);
  ht1632_sendcmd(m, HT1632_CMD_PWM | 0x0F); //pwm 16/16 (max)
  ht1632_sendcmd(m, HT1632_CMD_LEDON); 	/* LEDs on */
  
  //mySPI.releaseSelect();
}

void Titreur::ht1632_sendcmd (int chipNo, unsigned char command)
{
  
  int data=0;
  data = HT1632_ID_CMD;
  data <<= 8;
  data |= command;
  data <<= 5;
  //reverseEndian(&data, sizeof(data));
  
  unsigned char buff[2];
  buff[1]=data;
  buff[0]=data>>8;
  //fprintf(stderr, "data %X- %X %X-result %X %X\n",data,data,data>>8,buff[0],buff[1]);
  
   //mySPI.send(chipNo,(unsigned char *) &data,2);
  mySPI.send(chipNo,buff,2);

}

void Titreur::plot(int x,int y,int val){
  if (x>=0 && y>=0 && ((typeModule==MODULE_24x16 && y<16 && x<24*nb_module) || (typeModule==MODULE_32x8 && y<8 && x<32*nb_module))) {
    if (typeModule==MODULE_24x16) {
      if(y<8){
        if(val==1) *(matrix+x*2) |= val<<(7-y);
        if(val==0) *(matrix+x*2) &= ~(val<<(7-y));
      }
      else{
        if(val==1) *(matrix+x*2+1) |= val<<(7-(y-8));
        if(val==0) *(matrix+x*2+1) &= ~(val<<(7-(y-8)));
      }
    }
      if (typeModule==MODULE_32x8) {
          if(val==1) *(matrix+x) |= val<<(7-y);
          if(val==0) *(matrix+x) &= ~(val<<(7-y));
    }
  }
  //else fprintf(stderr, "outside area plot\n");
}


void Titreur::putChar(int x, int y, char c){
  fprintf(stderr, "%c(%u)",c,c);
  c-=32;

  for (char col=0; col< 6; col++) {
    int dots = myfont[c][col];
    for (char row=0; row < 8; row++) { // only 8 rows.
      if (dots & (128>>row)) plot(x+col, y+row, 1); else plot(x+col, y+row, 0);
    }
  }
}

void Titreur::text(int x, int y,char Str1[]){
  messageLength = cleanCharArray(Str1);
  fprintf(stderr,"%sdrawtext %u\n\r",debug.c_str(),messageLength);
  for (int i =0; i<messageLength ; i++){
    putChar(x+(i)*6, y,Str1[i]);
  }
    fprintf(stderr, "\n");
  printScreen();
}

int Titreur::cleanCharArray(char Str1[]){
  messageLength = strlen(Str1);
  int j=0;
  for (int i =0; i<messageLength  ; i++){
    unsigned char uc = (unsigned char)Str1[i];
    if (uc!=195 && uc!=197) {Str1[i-j]=Str1[i];
    } else if(uc==197){
      unsigned char uc2 = (unsigned char)Str1[i+1];
      if (uc2==146) Str1[i-j]=190;
      if (uc2==147) Str1[i-j]=189;
      i++;j++;
    } else{
      j++;
    }
  }
  return messageLength-j;
}


void Titreur::allLedOn(){
  for (int i=0; i<typeModule*nb_module; i++) {
    *(matrix+i)=0xff;
  }
  printScreen();
}

void Titreur::allLedOff(){
  flushMatrix();
  printScreen();
}


void Titreur::flushMatrix(){
  for (int i=0; i<typeModule*nb_module; i++) {
    *(matrix+i)=0;
  }
}



void Titreur::testScreen(){
  fprintf(stderr, "%stest titreur module\n",debug.c_str());
  for (int i=0; i<typeModule*nb_module; i++) {
      *(matrix+i)=i;
    }
  
  printScreen();
    
}

void Titreur::printScreen(){
  fprintf(stderr, "%sprint  %u",debug.c_str(),m);
  for (int m=0; m<nb_module; m++) {
  *output = 160;
  fprintf(stderr, "module %u",m);
  for (int i=0; i<typeModule+2; i++) {
    if (i==0) *(output+1) = 0 | ((*(matrix+typeModule*m)>>2)&63);
    else if (i==typeModule) *(output+i+1)= ((*(matrix+typeModule*m)>>2)&63) | ((*(matrix+(i-1+typeModule*m))<<6)&192);
    else if (i==typeModule+1) *(output+i+1) = ((*(matrix+1+typeModule*m)>>2)&63) | ((*(matrix+typeModule*m)<<6)&192);
    else *(output+i+1)=((*(matrix+(i-1+typeModule*m))<<6)&192) | ((*(matrix+i+typeModule*m)>>2)&63);
  }
  mySPI.send(m,output,typeModule+3);
  
}
  fprintf(stderr, "\n");
  
}

int Titreur::charbyline(){
  return nb_module*typeModule/6;
}


Titreur::~Titreur(){
  free(matrix);
  free(output);
}
