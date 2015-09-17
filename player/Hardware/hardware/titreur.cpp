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
#include <algorithm>

#include <string.h>
#include <sstream>
#include <iostream>

#include <time.h>
#include <sys/time.h>

/* TIME MEASURE */
unsigned long long mstime() {
	struct timeval tv;
  
	gettimeofday(&tv, NULL);
  
	unsigned long long millisecondsSinceEpoch =
  (unsigned long long)(tv.tv_sec) * 1000 +
  (unsigned long long)(tv.tv_usec) / 1000;
  
	return millisecondsSinceEpoch;
}

//init titreur
void Titreur::initTitreur(int _nb_module, int _typeModule){
  nb_module = _nb_module;
  typeModule = _typeModule;
  SPIspeed = 1000000;
  type = NO_SCROLL_NORMAL;
  needUpdate = 0;
  lastRefresh = mstime();
  mySPI.initSPI(SPIspeed);
  scrollSpeed = 500;
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
  delaytime = 250;
}



//problem, plutôt faire des commandes écrites pour être directement envoyée en SPI.

void Titreur::initModule(int m){
  fprintf(stderr, "\n\x1b[32mtitreur - init titreur module %u\n\x1b[0m",m);
  //mySPI.setkeepSelect();
  
  ht1632_sendcmd(m, HT1632_CMD_SYSDIS);  // Disable system
  //selectMappingType(m);
  ht1632_sendcmd(m, HT1632_CMD_MSTMD); 	/* Master Mode */
  ht1632_sendcmd(m, HT1632_CMD_RCCLK);  // HT1632C
  ht1632_sendcmd(m, HT1632_CMD_SYSON); 	/* System on */
  if (typeModule==MODULE_24x16) ht1632_sendcmd(m, HT1632_CMD_COMS01);
  if (typeModule==MODULE_32x8) ht1632_sendcmd(m, HT1632_CMD_COMS00);
  ht1632_sendcmd(m, HT1632_CMD_PWM | 0x0F); //pwm 16/16 (max)
  ht1632_sendcmd(m, HT1632_CMD_BLOFF);
  ht1632_sendcmd(m, HT1632_CMD_LEDON); 	/* LEDs on */
  
  //mySPI.releaseSelect();
}

//low level sending routine
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

//turn on/off one led on matrix
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

//put a char in matrix
void Titreur::putChar(int x, int y, char c){
  if(c!=0){//fprintf(stderr, "%c(%u)",c,c);
  c-=32;
  int cc=c;
  for (int col=0; col< 6; col++) {
    unsigned char dots = myfont[cc][col];
    for (char row=0; row < 8; row++) { // only 8 rows.
      if(big==0){
        if (dots & (128>>row)) plot(x+col, y+row, 1); else plot(x+col, y+row, 0);
      }else{
        if (dots & (128>>row)) {
          plot(x+col*2, y+row*2, 1);
          plot(x+col*2+1, y+row*2, 1);
          plot(x+col*2+1, y+row*2+1, 1);
          plot(x+col*2, y+row*2+1, 1);
        }else {
          plot(x+col*2, y+row*2, 0);
          plot(x+col*2+1, y+row*2, 0);
          plot(x+col*2+1, y+row*2+1, 0);
          plot(x+col*2, y+row*2+1, 0);
        }
      }
    }
  }
  }
}

//text on matrix + print on screen
void Titreur::text(int x, int y,char Str1[],int messageLength){
  messageLength = strlen(Str1) - cleanCharArray(Str1);
  //fprintf(stderr,"titreur - text (%u-%u):%s \n",messageLength,strlen(Str1),Str1);
  for (int i =0; i<messageLength ; i++){
    if(x+(i)*(6+6*big)>-6 && x+(i)*(6+6*big)<pixelbyline()+6)
      putChar(x+(i)*(6+6*big), y,Str1[i]);
  }
    //fprintf(stderr, "\n");
}

void Titreur::twolineText(std::string _line1, std::string _line2, int _type, int _speed){
  delaytime=_speed;
  line1.clear();
  line1=_line1;
  line2.clear();
  line2=_line2;
  type = _type;
  big = 0;
  if (type > 99) big = 1;
  needUpdate = 1;
  lastRefresh=mstime();
  xpos=0; ypos=0;
  fprintf(stderr,"titreur - drawtext type %u \n1(%u):%s \n2(%u):%s\n",type, line1.length(),line1.c_str(),line2.length(),line2.c_str());
}


void Titreur::updateText(){
  if (needUpdate>0) {
    flushMatrix();
    char buff_noscroll[charbyline()];
    char buff_line1[line1.length()+1];
    char buff_line2[line2.length()+1];
    int maxline = 0;
    if (line1.length()>line2.length()) maxline = line1.length();
    else maxline = line2.length();

    switch (type) {
      case NO_SCROLL_NORMAL:
        //fprintf(stderr,"titreur - updatetext type %u \n1(%u):%s \n2(%u):%s\n",type, line1.length(),line1.c_str(),line2.length(),line2.c_str());
        strncpy(buff_noscroll, line1.c_str(), sizeof(buff_noscroll));
        text(0,0,buff_noscroll,charbyline());
        strncpy(buff_noscroll, line2.c_str(), sizeof(buff_noscroll));
        text(0,8,buff_noscroll,charbyline());
        printScreen();
        needUpdate=0;
        break;
       
      case NO_SCROLL_BIG:
        //fprintf(stderr,"titreur - updatetext type %u \n1(%u):%s \n2(%u):%s\n",type, line1.length(),line1.c_str(),line2.length(),line2.c_str());
        strncpy(buff_noscroll, line1.c_str(), sizeof(buff_noscroll));
        text(0,0,buff_noscroll,charbyline());
        printScreen();
        needUpdate=0;
        break;
        
      case SCROLL_NORMAL:
        if (mstime()>lastRefresh+delaytime) {
          //fprintf(stderr,"titreur - updatetext type %u \n1(%u):%s \n2(%u):%s\n",type, line1.length(),line1.c_str(),line2.length(),line2.c_str());
          lastRefresh+=delaytime;
          if(xpos + 6 * maxline> 0){
            strncpy(buff_line1, line1.c_str(), sizeof(buff_line1));
            text(xpos,0,buff_line1,line1.length());
            strncpy(buff_line2, line2.c_str(), sizeof(buff_line2));
            text(xpos,8,buff_line2,line2.length());
            printScreen();
            xpos--;
          }else{
            needUpdate = 0;
            std::cout << "#TITREUR_SCROLL_END" << std::endl;
          }
        }
        break;
          
      case SCROLL_BIG:
        if (mstime()>lastRefresh+delaytime) {
          //fprintf(stderr,"titreur - updatetext type %u \n1(%u):%s \n2(%u):%s\n",type, line1.length(),line1.c_str(),line2.length(),line2.c_str());
          lastRefresh+=delaytime;
          if(xpos + 12 * maxline> 0){
            strncpy(buff_line1, line1.c_str(), sizeof(buff_line1));
            text(xpos,0,buff_line1,line1.length());
            printScreen();
            xpos--;
          }else{
            needUpdate = 0;
            std::cout << "#TITREUR_SCROLL_END" << std::endl;
          }
        }
        break;
        
      case SCROLL_LOOP_NORMAL:
        if (mstime()>lastRefresh+delaytime) {
          //fprintf(stderr,"titreur - updatetext type %u \n1(%u):%s \n2(%u):%s\n",type, line1.length(),line1.c_str(),line2.length(),line2.c_str());
          lastRefresh+=delaytime;
          if(xpos + 6 * maxline> 0){
            strncpy(buff_line1, line1.c_str(), sizeof(buff_line1));
            text(xpos,0,buff_line1,line1.length());
            strncpy(buff_line2, line2.c_str(), sizeof(buff_line2));
            text(xpos,8,buff_line2,line2.length());
            printScreen();
            xpos--;
          }else{
            xpos=0;
            std::cout << "#TITREUR_SCROLL_END" << std::endl;
          }
        }
        break;
        
      case SCROLL_LOOP_BIG:
        if (mstime()>lastRefresh+delaytime) {
          //fprintf(stderr,"titreur - updatetext type %u \n1(%u):%s \n2(%u):%s\n",type, line1.length(),line1.c_str(),line2.length(),line2.c_str());
          lastRefresh+=delaytime;
          if(xpos + 12 * maxline> 0){
            char buff[line1.length()];
            strncpy(buff, line1.c_str(), sizeof(buff));
            text(xpos,0,buff,line1.length());
            printScreen();
            xpos--;
          }else{
            xpos=0;
            std::cout << "#TITREUR_SCROLL_END" << std::endl;
          }
        }
        break;
        
      default:
        break;
    }
  }
}




//do some trick with special char
int Titreur::cleanCharArray(char Str1[]){
  int j=0;
  for (int i =0; i<strlen(Str1)  ; i++){
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
  return j;
}

//light screen
void Titreur::allLedOn(){
  for (int i=0; i<typeModule*nb_module; i++) {
    *(matrix+i)=0xff;
  }
  printScreen();
}

//clear screen
void Titreur::allLedOff(){
  flushMatrix();
  printScreen();
}

void Titreur::flushMatrix(){
  for (int i=0; i<typeModule*nb_module; i++) {
    *(matrix+i)=0;
  }
}


//use for debug
void Titreur::testScreen(){
  fprintf(stderr, "titreur - test titreur module\n");
  for (int i=0; i<typeModule*nb_module; i++) {
      *(matrix+i)=i;
    }
  
  printScreen();
    
}


//print matrix on screen
void Titreur::printScreen(){
  //fprintf(stderr, "titreur - print : ");
  for (int m=0; m<nb_module; m++) {
  *output = 160;
  //fprintf(stderr, "module %u",m);
  for (int i=0; i<typeModule+2; i++) {
    if (i==0) *(output+1) = 0 | ((*(matrix+typeModule*m)>>2)&63);
    else if (i==typeModule) *(output+i+1)= ((*(matrix+typeModule*m)>>2)&63) | ((*(matrix+(i-1+typeModule*m))<<6)&192);
    else if (i==typeModule+1) *(output+i+1) = ((*(matrix+1+typeModule*m)>>2)&63) | ((*(matrix+typeModule*m)<<6)&192);
    else *(output+i+1)=((*(matrix+(i-1+typeModule*m))<<6)&192) | ((*(matrix+i+typeModule*m)>>2)&63);
  }
  mySPI.send(m,output,typeModule+3);
  
}
  //fprintf(stderr, "\n");
  
}

//turn off ht1632
void Titreur::powerdown(){
  for (int i=0; i<nb_module; i++) {
    fprintf(stderr, "titreur - power down titreur module %u\n",i);
    ht1632_sendcmd(i, HT1632_CMD_SYSDIS);  // Disable system
  }
}

//nb of char by line
int Titreur::charbyline(){
  if(type<100)return nb_module*typeModule/6;
  else return nb_module*typeModule/12;
}

int Titreur::pixelbyline(){
    return nb_module*typeModule;
}

int Titreur::pixelHeight(){
  if(nb_module==MODULE_32x8)return 8;
  return 16;
}



//dealloc memory
Titreur::~Titreur(){
  free(matrix);
  free(output);
}
