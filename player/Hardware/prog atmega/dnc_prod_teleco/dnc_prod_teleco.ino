#include <avr/pgmspace.h>
#include "pins_arduino.h"
#include <LiquidCrystal595.h>
#include <Encoder.h>
#include <avr/sleep.h>
#include "printf.h"
#include "MemoryFree.h"






boolean simpleRemote =false;

//function for reset
void(* resetFunc) (void) = 0;


//------------------------------------ROTARY

//declare encoder
Encoder rotary(2, 3);
long positionLeft  = -999;


//------------------------------------LCD

//declare lcd
LiquidCrystal595 lcd(6, 7, 8);

#define LCD_PLAY 0
#define LCD_NEXT 1
#define LCD_REWIND 2
#define LCD_BACK 3
#define LCD_PAUSE 4
#define LCD_RELOAD 5
#define LCD_SYMBOL_DISCONNECT 6
#define LCD_SYMBOL_MINTIME 7

const byte character_data[8][8] PROGMEM= {
  { B00000,B10000,B11000,B11100,B11110,B11100,B11000,B10000},//play
  { B00000,B10001,B11001,B11101,B11111,B11101,B11001,B10001},//next
  { B00000,B00001,B00011,B00111,B01111,B00111,B00011,B00001},//rewind
  { B00000,B10001,B10011,B10111,B11111,B10111,B10011,B10001},//back
  { B00000,B00000,B11011,B11011,B11011,B11011,B11011,B00000},//pause
  { B00100,B00110,B11111,B10110,B10100,B10000,B10001,B01110},//reload
  { B00000, B01010, B11111, B11100, B10001, B00111, B01110, B00100 },
  { B10101, B00000, B00100, B01110, B10011, B10101, B10001, B01110 }
};

void initlcd(){
  printf_P(PSTR("init lcd"));
  lcd.begin(16, 2);
  byte my_character_data[8];
  for (byte i=0;i<8;i++) {
    memcpy_P (&my_character_data, &character_data[i], sizeof(my_character_data));
    lcd.createChar(i,my_character_data);
  }
  delay(5);
  lcd.display();
  lcd.setBackLight(1);
  printf_P(PSTR(" ok\n"));
  //printf_P(PSTR("free memory = %u \n"),freeMemory());
}

//-------------------------------REGISTER AND BUFFER


// what to do with incoming data
#define T_BUFFER_SIZE 38
volatile char buf [T_BUFFER_SIZE];  // buffer for receive string over spi
volatile byte pos;    //pos in the buffer
volatile byte command = 0;  // 2 bits command
volatile byte adress = 0;   // 6 bits adress

//VALUE FOR PINOUT
#define T_LEDRVALUE 0
#define T_LEDVVALUE 1
#define T_LEDOKVALUE 2
#define T_INTERRUPT 3
//VALUE FOR PININ
#define T_PUSHA 4
#define T_PUSHB 5
#define T_PUSHROTARY 6
#define T_PUSHOK 7
#define T_REED 8
//VALUE FOR PININ ANALOG
#define T_FLOAT 9
//meta
#define T_DISPLAY_LOCK 10
#define T_TELECOMODE 11
#define T_BOARDCHECKFLOAT 12
//ledstrob
#define T_STROBLRSPEED 13
#define T_STROBLVSPEED 14
#define T_STROBLOKSPEED 15

#define T_INIT 16
#define T_LOCK 17

#define T_STRING 18
#define T_POPUP 19
#define T_BUTON_STRING 20


//size of table
#define T_REGISTERSIZE 21

#define T_MODEBASE 1

//define two register
byte Value[T_REGISTERSIZE];
byte newValue[T_REGISTERSIZE];

//define PIN for each register
byte outpin[4] = {A5, A7, A0, 4};
#define T_DECINPIN 4
byte inpin[5] = {A2, A3, 5, A4, A1};
#define T_DECALALOGPIN 9
byte inpinanalog[1] = {A6};

//for timing purpose
long unsigned lastLRStrob;
byte strobLRStep;
long unsigned lastLVStrob;
byte strobLVStep;
long unsigned lastLOKStrob;
byte strobLOKStep;
// define checkinput cycle
long unsigned lastCheckInput;
int checkInputPeriod;
byte onePushRotary;
byte onePushA;
byte onePushB;
byte onePushOK;

long interruptTimeOn;
int timeOutInterrupt=1500;

void initpin() {
  printf_P(PSTR("init pin"));
  byte i = 0;
  for (i = 0; i < T_DECINPIN; i++) {
    pinMode(outpin[i], OUTPUT);
    updateValue(i);
  }
  for (i = T_DECINPIN; i < T_DECALALOGPIN; i++) {
    pinMode(inpin[i - T_DECINPIN], INPUT);
  }
  strobLRStep = 0;
  strobLVStep = 0;
  strobLOKStep = 0;
  printf_P(PSTR(" ok\n"));
  //printf_P(PSTR("free memory = %u \n"),freeMemory());
}


//flush buffer
void flushbuf(){
  printf_P(PSTR("flush buff\n"));
  for (byte i=0; i<T_BUFFER_SIZE-1; i++) {
    buf[i]=' ';
  }
  buf[T_BUFFER_SIZE-1]=0;
  pos = 0;
}

void clearRegister() {
  printf_P(PSTR("clear register\n"));
  for (byte i = 0; i < T_REGISTERSIZE; i++) {
    Value[i] = 0;
    newValue[i] = 0;
  }
}

boolean interruptPending(){
  if(Value[T_INTERRUPT] == 0)return false;
  return true;
}

void freeInterrupt(){
  newValue[T_INTERRUPT] = 0;
  Value[T_INTERRUPT] = newValue[T_INTERRUPT];
  digitalWrite(outpin[T_INTERRUPT], LOW);
}

void setInterrupt(byte interrupt){
  newValue[T_INTERRUPT] = interrupt;
  Value[T_INTERRUPT] = newValue[T_INTERRUPT];
  printf_P(PSTR("interupt %u\n"),Value[T_INTERRUPT]);
  interruptTimeOn = millis();
  digitalWrite(outpin[T_INTERRUPT], HIGH);
  SPDR = interrupt;
}

bool inputRange(byte i) {
  if (i >= T_DECINPIN && i < T_DECALALOGPIN + 1) return true;
  return false;
}

bool outputRange(byte i) {
  if (i < T_DECINPIN - 1) return true;
  return false;
}

//courbe pour adapter la luminosite

byte lightfunc(byte v) {
  if (v > 0)return HIGH;
  return LOW;
}

//gestion du changement de valeur sortie LED RVB et led 10W1

void updateValue(byte i) {
  Value[i] = newValue[i];
  digitalWrite(outpin[i], lightfunc(Value[i]));
}

//fonction pour generer une interuption sur le rpi
void updateInput(byte i) {
  if (!interruptPending()) {
    if(i==T_REED && newValue[i]==1) switchLock(255);
    Value[i] = newValue[i];
    setInterrupt(i);
  }
}


//stob sur la sortie LED R, LED V, LEDOK

void strobLRRoutine(byte force) {
  if (millis() > lastLRStrob + (10L * Value[T_STROBLRSPEED]) || force) {
    strobLRStep = (strobLRStep + 1) % 2;
    if (force)strobLRStep = 1;
    digitalWrite(outpin[T_LEDRVALUE], lightfunc(Value[T_LEDRVALUE]*strobLRStep));
    lastLRStrob += 10L * Value[T_STROBLRSPEED];
  }
}

void strobLVRoutine(byte force) {
  if (millis() > lastLVStrob + (10L * Value[T_STROBLVSPEED]) || force) {
    strobLVStep = (strobLVStep + 1) % 2;
    if (force)strobLVStep = 1;
    digitalWrite(outpin[T_LEDVVALUE], lightfunc(Value[T_LEDVVALUE]*strobLVStep));
    lastLVStrob += 10L * Value[T_STROBLVSPEED];
  }
}


//-------------------------------------------------lock teleco

#define T_ISOPEN 0
#define T_ISLOCK 1
#define T_ISLOCKWITHSLEEP 2
#define T_POWEROFF 10

void switchLock(byte force){
  if (simpleRemote) {
    simpleRemote=false;
  }else{
    printf_P(PSTR("switch lock (T_LOCK%u-%u) force %u - "),newValue[T_LOCK],Value[T_LOCK], force);
    if (Value[T_LOCK]==T_ISOPEN || force==T_ISLOCK){
      Value[T_LOCK]=T_ISLOCK; newValue[T_LOCK]=T_ISLOCK;
      pinMode(outpin[T_LEDRVALUE], INPUT);
      printf_P(PSTR("lock\n"));
      return;
    }
    if (Value[T_LOCK]==T_ISLOCK || force==T_ISLOCKWITHSLEEP){
      Value[T_LOCK]=T_ISLOCKWITHSLEEP; newValue[T_LOCK]=T_ISLOCKWITHSLEEP;
      pinMode(outpin[T_LEDRVALUE], INPUT);
      lcd.noDisplay();
      lcd.setBackLight(0);
      printf_P(PSTR("lock and sleep\n"));
      return;
    }
    if (Value[T_LOCK]==T_ISLOCKWITHSLEEP || force==T_ISOPEN){
      Value[T_LOCK]=T_ISOPEN; newValue[T_LOCK]=T_ISOPEN;
      pinMode(outpin[T_LEDRVALUE], OUTPUT);
      updateValue(T_LEDRVALUE);
      lcd.display();
      lcd.setBackLight(1);
      printf_P(PSTR("unlock\n"));
      return;
    }
    if (force==T_POWEROFF){
      Value[T_LOCK]=T_POWEROFF; newValue[T_LOCK]=T_POWEROFF;
      lcd.noDisplay();
      lcd.setBackLight(0);
      printf_P(PSTR("poweroff\n"));
      delay(5);
      poweroff();
      return;
    }
  }
}


//-------------------------------------------------new menu system

byte currentMenu=0;
int displayNeedUpdate=0;
byte popupNeedDisplay=0;
byte currentPopup=0;
long refreshMenu;
boolean show=true;

//menu struct saved in PROGMEM
typedef struct {
  char line1 [15]; //will be the same for all on the same hc595
  char line2 [15];
  byte behaviour;
  byte id;
  byte ok;
  byte b;
  byte a;
  boolean show;
  
  
} menutype;

#define T_MENU_BEHAVIOUR_MASTER 100
#define T_MENU_BEHAVIOUR_SHOW 1
#define T_MENU_BEHAVIOUR_SHOW2 2
#define T_MENU_BEHAVIOUR_LOG 20
#define T_MENU_BEHAVIOR_SELECT 30
#define T_MENU_BEHAVIOR_SELECT_DIFF 31
#define T_MENU_BEHAVIOR_SELECT_CONFIRM 32
#define T_MENU_BEHAVIOR_SETTINGS 31
#define T_MENU_BEHAVIOR_VOLUME 32
#define T_MENU_BEHAVIOR_STATUTS 50

#define T_MENU_LENGTH 46

//two variable objet to handle operation
menutype menu;
menutype temp;

//two line struct for saving string from pyton program
typedef struct {
  char line1 [17]; //will be the same for all on the same hc595
  char line2 [17];
} variableMenu;

#define T_MENU_ID_SHOW_STATUS 1
#define T_MENU_ID_STATUS_AUTO_NAME_IP_VOLTAGE 2
#define T_MENU_ID_STATUS_GIT_VERSION 3
#define T_MENU_ID_STATUS_SCENE 4
#define T_MENU_ID_STATUS_USB 5
#define T_MENU_ID_STATUS_MEDIA 6
#define T_MENU_ID_STATUS_SYNC 7
#define T_MENU_ID_STATUS_USER 8
#define T_MENU_ID_STATUS_ERROR 9

#define T_MENU_ID_LOG_0 10

#define T_MENU_NB_LOG 10

#define T_MENU_VARIABLE_LENGTH 25

#define TELECO_MESSAGE_PREVIOUSSCENE 1
#define TELECO_MESSAGE_PREVIOUSSCENE_GROUP 2
#define TELECO_MESSAGE_PREVIOUSSCENE_ALL_SYNC 3
#define TELECO_MESSAGE_RESTARTSCENE 4
#define TELECO_MESSAGE_RESTARTSCENE_GROUP 5
#define TELECO_MESSAGE_RESTARTSCENE_ALL_SYNC 6
#define TELECO_MESSAGE_NEXTSCENE 7
#define TELECO_MESSAGE_NEXTSCENE_GROUP 8
#define TELECO_MESSAGE_NEXTSCENE_ALL_SYNC 9

#define TELECO_MESSAGE_SETTINGS_LOG_DEBUG 20
#define TELECO_MESSAGE_SETTINGS_LOG_ERROR 21
#define TELECO_MESSAGE_SETTINGS_VOLPLUS 22
#define TELECO_MESSAGE_SETTINGS_VOLMOINS 23
#define TELECO_MESSAGE_SETTINGS_VOLSAVE 24
#define TELECO_MESSAGE_SETTINGS_VOLBACK 25

#define TELECO_MESSAGE_MODE_SHOW 30
#define TELECO_MESSAGE_MODE_REPET 31
#define TELECO_MESSAGE_MODE_DEBUG 32
#define TELECO_MESSAGE_LOG_ERROR 33
#define TELECO_MESSAGE_LOG_DEBUG 34

#define TELECO_MESSAGE_BLINKGROUP 40
#define TELECO_MESSAGE_TESTROUTINE 41

#define TELECO_MESSAGE_SYS_RESTARTPY 50
#define TELECO_MESSAGE_SYS_RESTARTWIFI 51
#define TELECO_MESSAGE_SYS_UPDATESYS 52
#define TELECO_MESSAGE_SYS_POWEROFF 53
#define TELECO_MESSAGE_SYS_REBOOT 54

#define TELECO_MESSAGE_GET_INFO 60

#define TELECO_MESSAGE_MEDIA_VOLPLUS 70
#define TELECO_MESSAGE_MEDIA_VOLPLUS_GROUP 71
#define TELECO_MESSAGE_MEDIA_VOLPLUS_ALL_SYNC 72
#define TELECO_MESSAGE_MEDIA_VOLMOINS 73
#define TELECO_MESSAGE_MEDIA_VOLMOINS_GROUP 74
#define TELECO_MESSAGE_MEDIA_VOLMOINS_ALL_SYNC 75
#define TELECO_MESSAGE_MEDIA_MUTE 76
#define TELECO_MESSAGE_MEDIA_MUTE_GROUP 77
#define TELECO_MESSAGE_MEDIA_MUTE_ALL_SYNC 78
#define TELECO_MESSAGE_MEDIA_PAUSE 79
#define TELECO_MESSAGE_MEDIA_PAUSE_GROUP 80
#define TELECO_MESSAGE_MEDIA_PLAY 81
#define TELECO_MESSAGE_MEDIA_PLAY_GROUP 82
#define TELECO_MESSAGE_MEDIA_STOP 83
#define TELECO_MESSAGE_MEDIA_STOP_GROUP 84




const menutype menulist[T_MENU_LENGTH] PROGMEM = {
  {" do not clean","     V1.4",T_MENU_BEHAVIOUR_MASTER,0,0,0,0,true},
  {"--SHOW","",T_MENU_BEHAVIOUR_MASTER,0,0,0,0,true},
  {"name + volt","OK  B  A",T_MENU_BEHAVIOUR_SHOW,T_MENU_ID_SHOW_STATUS,0,0,0,true},
  {"name + volt","OK  +  -",T_MENU_BEHAVIOUR_SHOW2,T_MENU_ID_SHOW_STATUS,0,0,0,true},
  {"--commande","scenario",T_MENU_BEHAVIOUR_MASTER,0,0,0,0,true},
  {"move next","solo group all",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_NEXTSCENE,TELECO_MESSAGE_NEXTSCENE_GROUP,TELECO_MESSAGE_NEXTSCENE_ALL_SYNC,true},
  {"move previous","solo group all",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_PREVIOUSSCENE,TELECO_MESSAGE_PREVIOUSSCENE_GROUP,TELECO_MESSAGE_PREVIOUSSCENE_ALL_SYNC,false},
  {"restart scene","solo group all",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_RESTARTSCENE,TELECO_MESSAGE_RESTARTSCENE_GROUP,TELECO_MESSAGE_RESTARTSCENE_ALL_SYNC,false},
  {"--commande","media",T_MENU_BEHAVIOUR_MASTER,0,0,0,0,true},
  {"volume plus","solo group all",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_MEDIA_VOLPLUS,TELECO_MESSAGE_MEDIA_VOLPLUS_GROUP,TELECO_MESSAGE_MEDIA_VOLPLUS_ALL_SYNC,true},
  {"volume moins","solo group all",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_MEDIA_VOLMOINS,TELECO_MESSAGE_MEDIA_VOLMOINS_GROUP,TELECO_MESSAGE_MEDIA_VOLMOINS_ALL_SYNC,true},
  {"mute","solo group all",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_MEDIA_MUTE,TELECO_MESSAGE_MEDIA_MUTE_GROUP,TELECO_MESSAGE_MEDIA_MUTE_ALL_SYNC,true},
  {"stop","solo group all",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_MEDIA_STOP,TELECO_MESSAGE_MEDIA_STOP_GROUP,0,false},
  {"pause","solo group all",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_MEDIA_PAUSE,TELECO_MESSAGE_MEDIA_PAUSE_GROUP,0,false},
  {"play","solo group all",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_MEDIA_PLAY,TELECO_MESSAGE_MEDIA_PLAY_GROUP,0,false},
  {"--settings","",T_MENU_BEHAVIOUR_MASTER,0,0,0,0,true},
    {"modes","show repe debu",T_MENU_BEHAVIOR_SELECT,0,TELECO_MESSAGE_MODE_SHOW,TELECO_MESSAGE_MODE_REPET,TELECO_MESSAGE_MODE_DEBUG,true},
    {"volume","    plus moins",T_MENU_BEHAVIOR_SELECT,0,0,TELECO_MESSAGE_SETTINGS_VOLPLUS,TELECO_MESSAGE_SETTINGS_VOLMOINS,false},
    {"volume memory","save back",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_SETTINGS_VOLSAVE,TELECO_MESSAGE_SETTINGS_VOLBACK,0,false},
    {"log level","error    debug",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_LOG_ERROR,0,TELECO_MESSAGE_LOG_DEBUG,false},
  {"--statuts","view info",T_MENU_BEHAVIOUR_MASTER,0,0,0,0,true},
  {"need_stat","name ip v",T_MENU_BEHAVIOR_STATUTS,T_MENU_ID_STATUS_AUTO_NAME_IP_VOLTAGE,0,0,0,true},
  {"need_stat","git version",T_MENU_BEHAVIOR_STATUTS,T_MENU_ID_STATUS_GIT_VERSION,0,0,0,true},
  {"need_stat","scene",T_MENU_BEHAVIOR_STATUTS,T_MENU_ID_STATUS_SCENE,0,0,0,true},
  {"need_stat","usb",T_MENU_BEHAVIOR_STATUTS,T_MENU_ID_STATUS_USB,0,0,0,true},
  {"need_stat","media",T_MENU_BEHAVIOR_STATUTS,T_MENU_ID_STATUS_MEDIA,0,0,0,true},
  {"need_stat","sync",T_MENU_BEHAVIOR_STATUTS,T_MENU_ID_STATUS_SYNC,0,0,0,true},
  {"need_stat","user",T_MENU_BEHAVIOR_STATUTS,T_MENU_ID_STATUS_USER,0,0,0,true},
  {"need_stat","error",T_MENU_BEHAVIOR_STATUTS,T_MENU_ID_STATUS_ERROR,0,0,0,true},
    {"--commande","syteme",T_MENU_BEHAVIOUR_MASTER,0,0,0,0,false},
    {"restart","PY wifi reboot",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_SYS_RESTARTPY,TELECO_MESSAGE_SYS_RESTARTWIFI,TELECO_MESSAGE_SYS_REBOOT,false},
    {"system","update     off",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_SYS_UPDATESYS,0,TELECO_MESSAGE_SYS_POWEROFF,false},
    {"test","routine  blink",T_MENU_BEHAVIOR_SELECT_CONFIRM,0,TELECO_MESSAGE_TESTROUTINE,0,TELECO_MESSAGE_BLINKGROUP,false},
  {"--logs","view history",T_MENU_BEHAVIOUR_MASTER,0,0,0,0,false},
  {"log","1",T_MENU_BEHAVIOUR_LOG,T_MENU_ID_LOG_0,0,0,0,false},
  {"log","2",T_MENU_BEHAVIOUR_LOG,T_MENU_ID_LOG_0+1,0,0,0,false},
  {"log","3",T_MENU_BEHAVIOUR_LOG,T_MENU_ID_LOG_0+2,0,0,0,false},
  {"log","4",T_MENU_BEHAVIOUR_LOG,T_MENU_ID_LOG_0+3,0,0,0,false},
  {"log","5",T_MENU_BEHAVIOUR_LOG,T_MENU_ID_LOG_0+4,0,0,0,false},
  {"log","6",T_MENU_BEHAVIOUR_LOG,T_MENU_ID_LOG_0+5,0,0,0,false},
  {"log","7",T_MENU_BEHAVIOUR_LOG,T_MENU_ID_LOG_0+6,0,0,0,false},
  {"log","8",T_MENU_BEHAVIOUR_LOG,T_MENU_ID_LOG_0+7,0,0,0,false},
  {"log","9",T_MENU_BEHAVIOUR_LOG,T_MENU_ID_LOG_0+8,0,0,0,false},
  {"log","10",T_MENU_BEHAVIOUR_LOG,T_MENU_ID_LOG_0+9,0,0,0,false}
};

variableMenu variableMenulist[T_MENU_VARIABLE_LENGTH];

char patchlog[T_MENU_NB_LOG];

//fill the string with initial string from PROGMEM
void initmenu(){
  printf_P(PSTR("init menu \n"));
  for (byte i=0;i<T_MENU_LENGTH;i++){
    memcpy_P (&menu, &menulist[i], sizeof(menutype));
    //printf_P(PSTR("menu %u"),i);
    //printf_P(PSTR(" id=%u "),menu.id);
    //printf_P(PSTR(" line1=%s"),menu.line1);
    //printf_P(PSTR(" line2=%s\n"),menu.line2);
    if (menu.id!=0) {
      memcpy(variableMenulist[menu.id].line1, &menu.line1, 16 );
      memcpy(variableMenulist[menu.id].line2, &menu.line2, 16 );
    }
  }
  for (byte j=0; j<T_MENU_NB_LOG; j++) {
    patchlog[j]=j;
  }
  printf_P(PSTR(" ok\n"));
  //printf_P(PSTR("free memory = %u \n"),freeMemory());
}

//display menu
void displayMenu(byte need=0){
  if((displayNeedUpdate>0 && millis() > refreshMenu + displayNeedUpdate) || need){
    if(need==0){if (switchlockCom(1))need=2;}
    if (need>0) {
      byte theMenu=currentMenu;
      if (popupNeedDisplay) {
        theMenu=currentPopup;
      }
      printf_P(PSTR("update menu %u"),currentMenu);
      //try
      //SPCR &= ~_BV(SPIE);//disable spi interrupt
      memcpy_P (&menu, &menulist[currentMenu], sizeof(menutype));
      //printf_P(PSTR("get behaviour =%u\n"),menu.behaviour);
      //printf_P(PSTR("get id =%u\n"),menu.id);
      //printf_P(PSTR("free memory = %u \n"),freeMemory());
      //printf_P(PSTR("get line1 =%s\n"),menu.line1);
      //printf_P(PSTR("get line2 =%s\n"),menu.line2);
      //delay(20);
      lcd.clear();
      if(menu.id!=0){
        if(menu.id>=T_MENU_ID_LOG_0){
          byte place= (T_MENU_NB_LOG+patchlog[0]-(menu.id-T_MENU_ID_LOG_0))%T_MENU_NB_LOG + T_MENU_ID_LOG_0;
          printf_P(PSTR(" log id=%u log place %u"),menu.id,place);
          lcd.setCursor(0, 0);
          lcd.print(variableMenulist[place].line1);
          lcd.setCursor(0, 1);
          lcd.print(variableMenulist[place].line2);
        }
        else{
          printf_P(PSTR(" variable id=%u"),menu.id);
        lcd.setCursor(0, 0);
        lcd.print(variableMenulist[menu.id].line1);
        lcd.setCursor(0, 1);
        lcd.print(variableMenulist[menu.id].line2);
        }
      } else {
        printf_P(PSTR(" fixe"));
        lcd.setCursor(0, 0);
        lcd.print(menu.line1);
        lcd.setCursor(0, 1);
        lcd.print(menu.line2);
      }
      printf_P(PSTR(" done\n"));
      displayNeedUpdate=0;
      //SPCR |= _BV(SPIE); //enable spi interrupt
      refreshMenu=millis();
      if(need==2)switchlockCom(0);
      if (popupNeedDisplay){
        popupNeedDisplay=0;
        displayNeedUpdate=2000;
      }
    }
  }
}

boolean displayShow(boolean menushow){
  if (show) {
    return menushow;
  } else {
    return true;
  }
}


//return to previous master menu
void goprevMasterMenu(){
  if (currentMenu>0) {
    printf_P(PSTR("find prev master"));
    for (byte i=currentMenu-1; i>=0; i--) {
      memcpy_P (&temp, &menulist [i], sizeof(menutype));
      printf_P(PSTR(" - menu %u"),i);
      if(temp.behaviour==T_MENU_BEHAVIOUR_MASTER && displayNeedUpdate==0 && displayShow(temp.show)){
        printf_P(PSTR(" master\n"));
        currentMenu=i;
        displayNeedUpdate=1;
        return;
      }
    }
    printf_P(PSTR("\n"));
  }
}

void goprevMenu(){
  memcpy_P (&temp, &menulist[currentMenu-1], sizeof(menutype));
  if (temp.behaviour!=T_MENU_BEHAVIOUR_MASTER && currentMenu>0 && displayShow(temp.show)) {
    currentMenu--;
    displayNeedUpdate=1;
  }
}

//go to next master menu
void gonextMasterMenu(){
  if (currentMenu<T_MENU_LENGTH-1){
    printf_P(PSTR("find next master"));
    for (byte i=currentMenu+1; i<T_MENU_LENGTH; i++) {
      memcpy_P (&temp, &menulist [i], sizeof(menutype));
      printf_P(PSTR(" - menu %u"),i);
      if(temp.behaviour==T_MENU_BEHAVIOUR_MASTER && displayNeedUpdate==0 && displayShow(temp.show)){
        printf_P(PSTR(" master\n"));
        currentMenu=i;
        displayNeedUpdate=1;
        return;
      }
    }
    printf_P(PSTR("\n"));
  }
}




void gonextMenu(){
  memcpy_P (&temp, &menulist[currentMenu+1], sizeof(menutype));
  if (temp.behaviour!=T_MENU_BEHAVIOUR_MASTER && currentMenu+1<T_MENU_LENGTH && displayShow(temp.show)) {
    currentMenu++;
    displayNeedUpdate=1;
  }
}




//checkinput and do something function the menu we are
void newcheckInput(){
  if (millis() > lastCheckInput + checkInputPeriod && !interruptPending()) {
    for (byte i = 0; i < T_DECALALOGPIN - T_DECINPIN; i++) {
      if(Value[T_LOCK]==T_ISOPEN || T_DECINPIN+i==T_REED){
        //if teleco is not lock
        switch (T_DECINPIN+i) {
            //push on rotary
          case T_PUSHROTARY:
            
            if(1-digitalRead(inpin[i])==1 && !simpleRemote){
              if (onePushRotary==0){
                onePushRotary=1;
                printf_P(PSTR("get push rotary\n"));
                switch (menu.behaviour) {
                  case T_MENU_BEHAVIOUR_MASTER:
                    currentMenu++;
                    displayNeedUpdate=1;
                    break;
                  default:
                    goprevMasterMenu();
                    break;
                }
              }
            }else{
              onePushRotary=0;
            }
            
            break;
            //push A
          case T_PUSHA:
            switch (menu.behaviour) {
              case T_MENU_BEHAVIOUR_SHOW:
                newValue[T_DECINPIN + i] = 1 - digitalRead(inpin[i]);
                break;
              case T_MENU_BEHAVIOR_SELECT:
                if(1-digitalRead(inpin[i])==1){
                  if (onePushA==0){
                    onePushA=1;
                    printf_P(PSTR("get pushA select %u\n"),menu.a);
                    newValue[T_PUSHROTARY]=menu.a;
                  }
                }else{
                  unselect();
                }
                break;
              case T_MENU_BEHAVIOR_SELECT_CONFIRM:
                if(1-digitalRead(inpin[i])==1){
                  if (onePushA==0){
                    onePushA=1;
                    printf_P(PSTR("get pushA want confirm %u\n"),menu.a);
                    confirm(T_PUSHA,menu.a);
                  }
                }else{
                  unselect();
                }
                break;
              default:
                break;
            }
            break;
            //push b
          case T_PUSHB:
            //printf_P(PSTR("get pushB\n"));
            switch (menu.behaviour) {
              case T_MENU_BEHAVIOUR_SHOW:
                newValue[T_DECINPIN + i] = 1 - digitalRead(inpin[i]);
                break;
              case T_MENU_BEHAVIOR_SELECT:
                if(1-digitalRead(inpin[i])==1){
                  if (onePushB==0){
                    onePushB=1;
                    printf_P(PSTR("get pushB select %u\n"),menu.b);
                    newValue[T_PUSHROTARY]=menu.b;
                  }
                }else{
                  unselect();
                }
                break;
              case T_MENU_BEHAVIOR_SELECT_CONFIRM:
                if(1-digitalRead(inpin[i])==1){
                  if (onePushB==0){
                    onePushB=1;
                    printf_P(PSTR("get pushB want confirm %u\n"),menu.b);
                    confirm(T_PUSHB,menu.b);
                  }
                }else{
                  unselect();
                }
                break;
              default:
                break;
            }
            break;
            //push ok
          case T_PUSHOK:
            //printf_P(PSTR("get pushOK\n"));
            switch (menu.behaviour) {
              case T_MENU_BEHAVIOUR_SHOW:
                newValue[T_DECINPIN + i] = 1 - digitalRead(inpin[i]);
                break;
              case T_MENU_BEHAVIOR_SELECT:
                if(1-digitalRead(inpin[i])==1){
                  if (onePushOK==0){
                    onePushOK=1;
                    printf_P(PSTR("get pushOK select %u\n"),menu.ok);
                    newValue[T_PUSHROTARY]=menu.ok;
                  }
                }else{
                  unselect();
                }
                break;
              case T_MENU_BEHAVIOR_SELECT_CONFIRM:
                if(1-digitalRead(inpin[i])==1){
                  if (onePushOK==0){
                    onePushOK=1;
                    printf_P(PSTR("get pushOK select %u\n"),menu.ok);
                    confirm(T_PUSHOK,menu.ok);
                  }
                }else{
                  unselect();
                }
                break;
              default:
                break;
            }
            break;
            //reed
          case T_REED:
            newValue[T_DECINPIN + i] = 1 - digitalRead(inpin[i]);
            break;
        }
      }
    }
    //check analog
    if (Value[T_BOARDCHECKFLOAT] == 1) newValue[T_FLOAT] = map(analogRead(inpinanalog[T_FLOAT - T_DECALALOGPIN]), 0, 1024, 0, 255);
    
    //check rotary
    if(Value[T_LOCK]==T_ISOPEN){
      long newLeft;
      newLeft = (long)rotary.read()*1.0/2;
      if (newLeft!=positionLeft && !simpleRemote) {
        printf_P(PSTR("get rotary\n"));
        if (menu.behaviour==T_MENU_BEHAVIOUR_MASTER) {
          if (newLeft<positionLeft) goprevMasterMenu();
          else gonextMasterMenu();
        } else {
          if (newLeft<positionLeft) goprevMenu();
          else gonextMenu();
        }
        positionLeft=newLeft;
      }
    }
    lastCheckInput = millis();
  }
}

void confirm(byte button,byte val){
  lcd.setCursor(0, 1);
  lcd.print("  confirm ");
  boolean wait=true;
  while(wait){
    if(1-digitalRead(inpin[button])==0){
      lcd.setCursor(0, 1);
      lcd.print(menu.line2);
      wait=false;
    }
    if(1-digitalRead(inpin[T_PUSHROTARY])==1){
      newValue[T_PUSHROTARY]=val;
      lcd.print("OK");
      delay(100);
      lcd.setCursor(0, 1);
      lcd.print(menu.line2);
      wait=false;
      if (val==TELECO_MESSAGE_MODE_SHOW) {
        show=true;
      }
      if (val==TELECO_MESSAGE_MODE_REPET || val==TELECO_MESSAGE_MODE_DEBUG) {
        show=false;
      }
    }
  }
}

void unselect(){
  newValue[T_PUSHROTARY]=0;
  onePushOK=0;
  onePushB=0;
  onePushA=0;
}

void shiftlog(){
  printf_P(PSTR("shift logs\n"));
  for (byte i=0; i<T_MENU_NB_LOG; i++) {
    patchlog[i] = (patchlog[i]+1)%T_MENU_NB_LOG;
  }
}

void clearlines(byte i){
  for (byte j=0;j<16;j++){
    variableMenulist[i].line1[j]=' ';
    variableMenulist[i].line2[j]=' ';
  }
}

//checkstring receive
void newcheckStringReceive() {
  if (command == 0 && adress == T_STRING) {
    buf [pos] = 0;
    pos = 0;
    adress = 0;
    //if (!simpleRemote) {
    byte id = buf[0];
    //for log only
    if (id==T_MENU_ID_LOG_0) {
      shiftlog();
      byte place=T_MENU_ID_LOG_0+patchlog[0];
      printf_P(PSTR("get new log n=%u : %s store at place %u\n"),id,&buf[1],place);
      clearlines(place);
      copybuffer(variableMenulist[place].line1,1,16);
      copybuffer(variableMenulist[place].line2,17,16);
      displayNeedUpdate=300;
    }else{
      printf_P(PSTR("get new status n=%u : %s\n"),id,&buf[1]);
      clearlines(id);
      //fil menu with string
      //memcpy(&variableMenulist[id].line1[0], &buf[1], 16 );
      copybuffer(variableMenulist[id].line1,1,16);
      //memcpy(&variableMenulist[id].line2[0], &buf[17], 16 );
      copybuffer(variableMenulist[id].line2,17,16);
    }
    refreshMenu=millis();
    if (menu.id==id || menu.id>=T_MENU_ID_LOG_0) {
      printf_P(PSTR("same menu or log %u, need update\n"),id);
      displayNeedUpdate=300;
    }
    /*if (id>=T_MENU_ID_STATUS_USB && id<=T_MENU_ID_STATUS_ERROR) {
     popupNeedDisplay=1;
     displayNeedUpdate=60;
     currentPopup=id;
     }*/
    //flushbuf();
    //digitalWrite(outpin[T_INTERRUPT], LOW);
    //}
  }
}

boolean copybuffer(char* mystring,byte start,byte size){
  for (byte i=0; i<size; i++) {
    if (buf[i+start]==0) return false;
    mystring[i]=buf[i+start];
  }
  return true;
}

boolean switchlockCom(byte lock){
  if (!interruptPending()) {
    printf_P(PSTR("want lock com %u \n"),lock);
    newValue[T_DISPLAY_LOCK]=lock;
    Value[T_DISPLAY_LOCK]=lock;
    setInterrupt(T_DISPLAY_LOCK);
    while (interruptPending()) {
      lowleveRoutine();
    }
    printf_P(PSTR(" lock com ok\n"));
    return true;
  }
  return false;
}


//-------------------------------SPI

#define READCOMMAND 0x40
#define WRITECOMMANDVALUE 0xc0
#define WRITECOMMANDFADE 0x80
#define COMMANDMASK 0xC0

void initSPIslave() {
  printf_P(PSTR("init spi"));
  // have to send on master in, *slave out*
  pinMode(MISO, OUTPUT);
  // turn on SPI in slave mode
  SPCR |= _BV(SPE);
  // turn on interrupts
  SPCR |= _BV(SPIE);
  SPDR = 0;
  printf_P(PSTR(" ok\n"));
  //printf_P(PSTR("free memory = %u \n"),freeMemory());
  
}

// SPI interrupt routine
ISR (SPI_STC_vect)
{
  byte c = SPDR;
  //printf_P(c, HEX);
  
  if (command < 10) {
    //printf_P(PSTR("R add"));
    adress = c & ~COMMANDMASK;
    //printf_P(adress, HEX);
    //printf_P(PSTR(" com"));
    command = c & COMMANDMASK;
    //printf_P(command, HEX);
  } else {
    //valeur
    if (command == WRITECOMMANDVALUE) {
      if (adress < T_STRING) {
        printf_P(PSTR("wv %u=%u\n"),adress,c);
        newValue[adress] = c;
        command = 1;
        SPDR = 0;
      } else {//case string received
        if (pos < sizeof buf) {
          buf [pos++] = c;
        }
        return;
      }
    }
  }
  
  //renvoie la valeur enregistree
  if (command == READCOMMAND) {
    SPDR = Value[adress];
    command = 1;
    if (adress==Value[T_INTERRUPT]) {
      freeInterrupt();
    }
    printf_P(PSTR("read %u\n"),Value[adress]);
  }
}  // end of interrupt service routine (ISR) SPI_STC_vect




//-------------------------------main program

void setup (void) {
  Serial.begin(115200);
  printf_begin();
  printf_P(PSTR("teleco start\n"));
  clearRegister();
  initpin();
  initlcd();
  initSPIslave();
  checkInputPeriod = 100;
  flushbuf();
  initmenu();
  displayMenu(1);
  waitforinit();
  displayNeedUpdate=1000;
  currentMenu=2;
  positionLeft = rotary.read();
  printf_P(PSTR("init ok\n"));
}



void waitforinit(){
  printf_P(PSTR("\n wait for init\n"));
  delay(300);
  SPDR = 0;
  while(newValue[T_INIT]==0){
    setInterrupt(T_INIT);
    long time=millis();
    while(millis()<time+500 && newValue[T_INIT]==0){
      lowleveRoutine();
    }
    freeInterrupt();
  }
  delay(100);
}


void lowleveRoutine(){
  //if slave select not active
  if (digitalRead (SS) == HIGH) command = 0;
  //timeout if prog do not answer to interrupt
  if (interruptPending() && millis()>interruptTimeOn+timeOutInterrupt && Value[T_INIT]==1) {
    printf_P(PSTR("warning interrupt read fail\n"));
    newValue[T_LEDRVALUE] = 0;
    freeInterrupt();
  }
  newcheckStringReceive();
}



//boucle principale
void loop (void) {
  
  lowleveRoutine();
  
  //verification changement de valeur
  if (command == 0 && adress < T_STRING) {
    for (byte i = 0; i < T_REGISTERSIZE; i++) {
      if (Value[i] != newValue[i]) {
        if(newValue[T_INIT]==0) resetFunc();
        if (outputRange(i)) updateValue(i); //cas led output
        else if (inputRange(i)) {updateInput(i);}
        else {
          //cas autre valeur (sans fade)
          Value[i] = newValue[i];
          //cas particulier
          if (i == T_STROBLRSPEED)lastLRStrob = millis();
          if (i == T_STROBLRSPEED && Value[i] == 0) strobLRRoutine(1);
          if (i == T_STROBLVSPEED)lastLVStrob = millis();
          if (i == T_STROBLVSPEED && Value[i] == 0) strobLVRoutine(1);
          if (i == T_LOCK) switchLock(newValue[i]);
          
        }
      }
    }
  }
  if (Value[T_STROBLRSPEED] > 0) strobLRRoutine(0);
  if (Value[T_STROBLVSPEED] > 0) strobLVRoutine(0);
  
  newcheckInput();
  displayMenu();
  
}  // end of loop


//go deep sleep
void poweroff(){
  pinMode(outpin[T_LEDRVALUE], INPUT);
  // disable ADC
  ADCSRA = 0;
  set_sleep_mode (SLEEP_MODE_PWR_DOWN);
  sleep_enable();
  while(1)sleep_cpu ();
}










