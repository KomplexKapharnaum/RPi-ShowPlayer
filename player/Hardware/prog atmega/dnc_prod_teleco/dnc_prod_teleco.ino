#include "pins_arduino.h"
#include "pins_arduino.h"
#include <LiquidCrystal595.h>
#include <Encoder.h>
#include <avr/sleep.h>

char buf [68];
char line1 [17];
char line2 [17];
char line3 [17];
char line4 [17];
char popline1 [3][32];
char popline2 [3][32];
char buttonline [17];
int nbmenuinfo =5;
bool scroll=false;
long timescroll=millis();
long timescrollinterval=400;


Encoder rotary(2, 3);
long positionLeft  = -999;


LiquidCrystal595 lcd(6, 7, 8);


// what to do with incoming data
volatile byte pos;
volatile byte command = 0;
volatile byte adress = 0;



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
#define T_COUNTVAL 10
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
//size of menu
#define T_NBMENU 10

#define READCOMMAND 0x40
#define WRITECOMMANDVALUE 0xc0
#define WRITECOMMANDFADE 0x80
#define COMMANDMASK 0xC0

#define T_DECINPIN 4
#define T_DECALALOGPIN 9

#define T_MODEBASE 1

#define T_ISOPEN 0
#define T_ISLOCK 1
#define T_ISLOCKWITHSLEEP 2
#define T_POWEROFF 10



char menu[T_NBMENU][16] = {"previous scene","restart scene","next scene","blink group","restart py","restart wifi","update sys","poweroff","reboot","test routine"};

byte Value[T_REGISTERSIZE];
byte newValue[T_REGISTERSIZE];

byte outpin[4] = {A5, A7, A0, 4};

byte inpin[5] = {A2, A3, 5, A4, A1};

byte inpinanalog[1] = {A6};

long unsigned lastLRStrob;
byte strobLRStep;
long unsigned lastLVStrob;
byte strobLVStep;
long unsigned lastLOKStrob;
byte strobLOKStep;


long unsigned lastCheckInput;
int checkInputPeriod;

void(* resetFunc) (void) = 0;

void setup (void) {
  Serial.begin(19200);
  clearRegister();
  initpin();
  initSPIslave();
  Serial.println("telec");
  checkInputPeriod = 100;
  waitforinit();
  positionLeft = rotary.read();
  Serial.println("init");
}

void initpin() {
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
  
  pos = 0;   // buffer empty
  lcd.begin(16, 2);
#define LCD_PLAY 0
#define LCD_NEXT 1
#define LCD_REWIND 2
#define LCD_BACK 3
#define LCD_PAUSE 4
#define LCD_RELOAD 5
#define LCD_SYMBOL_DISCONNECT 6
#define LCD_SYMBOL_MINTIME 7
  byte character_data[8][8] = {
    { B00000,B10000,B11000,B11100,B11110,B11100,B11000,B10000},//play
    { B00000,B10001,B11001,B11101,B11111,B11101,B11001,B10001},//next
    { B00000,B00001,B00011,B00111,B01111,B00111,B00011,B00001},//rewind
    { B00000,B10001,B10011,B10111,B11111,B10111,B10011,B10001},//back
    { B00000,B00000,B11011,B11011,B11011,B11011,B11011,B00000},//pause
    { B00100,B00110,B11111,B10110,B10100,B10000,B10001,B01110},//reload
    { B00000, B01010, B11111, B11100, B10001, B00111, B01110, B00100 },
    { B10101, B00000, B00100, B01110, B10011, B10101, B10001, B01110 }
  };
  for (byte i=0;i<8;i++) {
    lcd.createChar(i,character_data[i]);
  }
  lcd.setCursor(0, 0);
  lcd.write(LCD_PLAY);
  lcd.print(" do not clean ");
  lcd.write(LCD_REWIND);
  lcd.setCursor(0, 1);
  lcd.print("      V0.5      ");
  lcd.setBackLight(1);
}

void scrollteleco(){
  if(scroll){
    if(millis()-timescrollinterval>timescroll){
      lcd.scrollDisplayLeft();
      timescroll=millis();
    }
  }
}

void clearRegister() {
  for (byte i = 0; i < T_REGISTERSIZE; i++) {
    Value[i] = 0;
    newValue[i] = 0;
  }
  
}

void initSPIslave() {
  // have to send on master in, *slave out*
  pinMode(MISO, OUTPUT);
  // turn on SPI in slave mode
  SPCR |= _BV(SPE);
  // turn on interrupts
  SPCR |= _BV(SPIE);
  SPDR = 0;
}

void waitforinit(){
  delay(500);
  SPDR = 0;
  digitalWrite(outpin[T_INTERRUPT], HIGH);
  while(command==0)scrollteleco();
  digitalWrite(outpin[T_INTERRUPT], LOW);
  Value[T_INIT]=1;
  newValue[T_INIT]=1;
}


// SPI interrupt routine
ISR (SPI_STC_vect)
{
  byte c = SPDR;
  //Serial.println(c, HEX);
  
  if (command < 10) {
    //Serial.print("R add");
    adress = c & ~COMMANDMASK;
    //Serial.print(adress, HEX);
    //Serial.print(" com");
    command = c & COMMANDMASK;
    //Serial.println(command, HEX);
  } else {
    //valeur
    if (command == WRITECOMMANDVALUE) {
      //Serial.println ("wv");
      if (adress < T_STRING) {
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
    if (inputRange(adress)) {
      newValue[T_INTERRUPT] = 0;
      Value[T_INTERRUPT] = newValue[T_INTERRUPT];
      digitalWrite(outpin[T_INTERRUPT], LOW);
    }
    Serial.print("r ");
    Serial.println (Value[adress],DEC);
  }
  
  
  
  
}  // end of interrupt service routine (ISR) SPI_STC_vect


//boucle principale

void loop (void) {
  
  // if SPI not active, clear current command
  if (digitalRead (SS) == HIGH) command = 0;
  
  //verification changement de valeur
  if (command == 0 && adress < T_STRING) {
    for (byte i = 0; i < T_REGISTERSIZE; i++) {
      if (Value[i] != newValue[i]) {
        if(newValue[T_INIT]==0) resetFunc();
        if (outputRange(i)) updateValue(i); //cas led output
        if (inputRange(i)) updateInput(i);
        else {
          //cas autre valeur (sans fade)
          Value[i] = newValue[i];
          Serial.print(millis(), DEC);
          Serial.print(" new ");
          Serial.print(i, DEC);
          Serial.print(" - v ");
          Serial.println(Value[i], DEC);
          
          
          //cas particulier
          if (i == T_STROBLRSPEED)lastLRStrob = millis();
          if (i == T_STROBLRSPEED && Value[i] == 0) strobLRRoutine(1);
          if (i == T_STROBLVSPEED)lastLVStrob = millis();
          if (i == T_STROBLVSPEED && Value[i] == 0) strobLVRoutine(1);
          if (i == T_LOCK) switchLock(Value[i]);
          
          
        }
      }
    }
  }
  
  
  if (Value[T_STROBLRSPEED] > 0) strobLRRoutine(0);
  if (Value[T_STROBLVSPEED] > 0) strobLVRoutine(0);
  //if (Value[T_STROBLVSPEED] > 0) strobLVRoutine();
  checkStringReceive();
  checkInput();
  scrollteleco();
  
}  // end of loop

void checkStringReceive() {
  if (command == 0 && adress == T_STRING) {
    buf [pos] = 0;
    Serial.println (buf);
    memcpy( line1, &buf[0], 16 );
    memcpy( line2, &buf[16], 16 );
    memcpy( line3, &buf[32], 16 );
    memcpy( line4, &buf[48], 16 );
    pos = 0;
    adress = 0;
  }
  if (command == 0 && adress == T_POPUP) {
    buf [pos] = 0;
    Serial.println (buf);
    lcd.clear();
    char temp[33];
    memcpy(temp ,&buf[0], 32);
    byte var=0;
    if (temp[0]=='1')
      var=1;
    if (temp[0]=='2')
      var=2;
      
    memcpy(popline1[var], &buf[0], 32 );
    memcpy(popline2[var], &buf[16], 32 );
    lcd.setCursor(0, 0);
    lcd.print(popline1[var]);
    lcd.setCursor(0, 1);
    lcd.print(popline2[var]);
    pos = 0;
    adress = 0;
    scroll=true;
  }
  if (command == 0 && adress == T_BUTON_STRING) {
    buf [pos] = 0;
    Serial.println (buf);
    memcpy(buttonline, &buf[0], 16 );
    pos = 0;
    adress = 0;
  }
}



bool inputRange(byte i) {
  if (i >= T_DECINPIN && i < T_DECALALOGPIN + 1) return true;
  return false;
}

bool outputRange(byte i) {
  if (i < T_DECINPIN - 1) return true;
  return false;
}


//fonction pour generer une interuption sur le rpi
void updateInput(byte i) {
  if (Value[T_INTERRUPT] == 0) {
    if(i==T_REED && newValue[i]==1) switchLock(255);
    Value[i] = newValue[i];
    newValue[T_INTERRUPT] = i;
    Value[T_INTERRUPT] = newValue[T_INTERRUPT];
    Serial.print ("interupt ");
    Serial.println(Value[T_INTERRUPT]);
    digitalWrite(outpin[T_INTERRUPT], HIGH);
    SPDR = i;
  }
}

void switchLock(byte force){
  if (Value[T_LOCK]==T_ISOPEN || force==T_ISLOCK){
    Value[T_LOCK]=T_ISLOCK; newValue[T_LOCK]=T_ISLOCK;
    pinMode(outpin[T_LEDRVALUE], INPUT);
    Serial.println ("lock");
    return;
  }
  if (Value[T_LOCK]==T_ISLOCK || force==T_ISLOCKWITHSLEEP){
    Value[T_LOCK]=T_ISLOCKWITHSLEEP; newValue[T_LOCK]=T_ISLOCKWITHSLEEP;
    pinMode(outpin[T_LEDRVALUE], INPUT);
    lcd.noDisplay();
    lcd.setBackLight(0);
    Serial.println ("lock and sleep");
    return;
  }
  if (Value[T_LOCK]==T_ISLOCKWITHSLEEP || force==T_ISOPEN){
    Value[T_LOCK]=T_ISOPEN; newValue[T_LOCK]=T_ISOPEN;
    pinMode(outpin[T_LEDRVALUE], OUTPUT);
    updateValue(T_LEDRVALUE);
    lcd.display();
    lcd.setBackLight(1);
    Serial.println ("unlock");
    return;
  }
  if (force==T_POWEROFF){
    Value[T_LOCK]=T_POWEROFF; newValue[T_LOCK]=T_POWEROFF;
    updateValue(T_LEDRVALUE);
    lcd.noDisplay();
    lcd.setBackLight(0);
    Serial.println ("poweroff");
    poweroff();
    return;
  }
}

void poweroff(){
  for (byte i = 0; i <= A5; i++)
  {
    pinMode (i, OUTPUT);    // changed as per below
    digitalWrite (i, LOW);  //     ditto
  }
  pinMode(outpin[T_LEDRVALUE], INPUT);
  // disable ADC
  ADCSRA = 0;
  set_sleep_mode (SLEEP_MODE_PWR_DOWN);
  sleep_enable();
  while(1)sleep_cpu ();
}



void checkInput() {
  if (millis() > lastCheckInput + checkInputPeriod) {
    //boutons
    for (byte i = 0; i < T_DECALALOGPIN - T_DECINPIN; i++) {
      if(Value[T_LOCK]==T_ISOPEN || T_DECINPIN+i==T_REED){
        if(T_DECINPIN+i==T_PUSHROTARY){
          if( 1-digitalRead(inpin[i])==1) {
            if (abs(positionLeft)%(T_NBMENU+nbmenuinfo)<T_NBMENU){
              newValue[T_DECINPIN + i] = abs(positionLeft)%(T_NBMENU+nbmenuinfo)+1;
            }else {
              newValue[T_DECINPIN + i] =250;
            }
          }else {
            newValue[T_DECINPIN + i] =0;
          }
        }else{
          newValue[T_DECINPIN + i] = 1 - digitalRead(inpin[i]);
          //Serial.print("b");
          //Serial.println(i, DEC);
        }
      }else{
         if(Value[T_LOCK]==T_ISOPEN) newValue[T_DECINPIN + i] = 1 - digitalRead(inpin[i]);
        }
      }
    
    //if (Value[T_BOARDCHECKFLOAT] == 1) newValue[T_FLOAT] = map(analogRead(inpinanalog[T_FLOAT - T_DECALALOGPIN]), 0, 1024, 0, 255);
    
    if(Value[T_LOCK]==T_ISOPEN){
      long newLeft;
      newLeft = (long)rotary.read()*1.0/2;
      if (newLeft > T_NBMENU+nbmenuinfo-1 || newLeft < 0) {
        newLeft=positionLeft;
        rotary.write(positionLeft*2);
      }
      if (newLeft != positionLeft) {
        scroll=false;
        lcd.clear();
        if(abs(newLeft)%(T_NBMENU+nbmenuinfo) == T_NBMENU){
          lcd.setCursor(0, 0);
          lcd.print(line1);
          lcd.setCursor(0, 1);
          lcd.print(line2);
        }else if(abs(newLeft)%(T_NBMENU+nbmenuinfo) == T_NBMENU+1){
          lcd.setCursor(0, 0);
          lcd.print(line3);
          lcd.setCursor(0, 1);
          lcd.print(line4);
        }else if(abs(newLeft)%(T_NBMENU+nbmenuinfo) == T_NBMENU+2){
          lcd.setCursor(0, 0);
          lcd.print(popline1[0]);
          lcd.setCursor(0, 1);
          lcd.print(popline2[0]);
          scroll=true;
        }else if(abs(newLeft)%(T_NBMENU+nbmenuinfo) == T_NBMENU+3){
          lcd.setCursor(0, 0);
          lcd.print(popline1[1]);
          lcd.setCursor(0, 1);
          lcd.print(popline2[1]);
          scroll=true;
        }else if(abs(newLeft)%(T_NBMENU+nbmenuinfo) == T_NBMENU+4){
          lcd.setCursor(0, 0);
          lcd.print(popline1[2]);
          lcd.setCursor(0, 1);
          lcd.print(popline2[2]);
          scroll=true;
        }else{
          lcd.setCursor(0, 0);
          lcd.print(menu[abs(newLeft)%(T_NBMENU+2)]);
          lcd.setCursor(0, 1);
          for(byte i=0;i<16;i++){
            if (buttonline[i]<'0' || buttonline[i]>'9') {
              lcd.print(buttonline[i]);
            }else{
              lcd.write(buttonline[i]-48);
            }
          }
        }
        positionLeft = newLeft;
      }
    }
    
    lastCheckInput = millis();
  }
  
}



//courbe pour adapter la luminosite

byte lightfunc(byte v) {
  if (v > 0)return HIGH;
  return LOW;
}

//gestion du changement de valeur sortie LED RVB et led 10W1

void updateValue(byte i) {
  Value[i] = newValue[i];
  /*Serial.print(millis(), DEC);
   Serial.print(" new ");
   Serial.print(i, DEC);
   Serial.print(" - v ");
   Serial.println(Value[i], DEC);*/
  digitalWrite(outpin[i], lightfunc(Value[i]));
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



