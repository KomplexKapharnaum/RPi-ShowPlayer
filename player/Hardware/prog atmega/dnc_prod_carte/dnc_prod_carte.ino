#include "pins_arduino.h"
#include <avr/sleep.h>


// what to do with incoming data
byte command = 0;
byte adress = 0;


//VALUE FOR PINOUT
#define LEDRVALUE 0
#define LEDVVALUE 1
#define LEDBVALUE 2
#define LED10W1VALUE 3
#define LED10W2VALUE 4
#define INTERRUPT 5
//VALUE FOR PININ
#define PUSH1 6
#define PUSH2 7
#define PUSH3 8
//VALUE FOR PININ ANALOG
#define FLOAT 9
#define UBATT 10
#define CODE 11
//RVB
#define LEDRVBSTROBSPEED 12
#define LEDRVBMODE 13
//GYRO
#define GYROMODE 14
#define GYROSPEED 15
#define GYROSTROBSPEED 16
//10W
#define LED10W1STROBSPEED 17
#define LED10W2STROBSPEED 18
//meta
#define BOARDMODE 19
#define PWMMODE 20
#define INIT 21
#define VOLTAGEMODE 22
#define BOARDCHECKFLOAT 23
#define POWERDOWN 24

//size of table
#define REGISTERSIZE 25

#define READCOMMAND 0x40
#define WRITECOMMANDVALUE 0xc0
#define WRITECOMMANDFADE 0x80
#define COMMANDMASK 0xC0

#define DECINPIN 6
#define DECALALOGPIN 9

#define GYROALLON 1
#define GYROALLOFF 0
#define GYRORIGHT 2
#define GYROLEFT 3

#define BOARDMODE_MANUALLIGHT 0
#define BOARDMODE_AUTOLIGHT 1

byte manuallightPos=0;
byte manuallightPosGyro=0;
byte manuallightPos10w=0;
byte manuallightPosStep=9;
byte manuallightPosGyroStep=2;
byte manuallightPos10wStep=2;


byte manuallightConduite[9][3]={
  {0,0,0},
  {0,0,255}, //bleu
  {255,75,0}, //orange
  {0,255,255}, //cyan
  {255,0,0},//rouge
  {0,0,0},
  {0,255,0}, //vert
  {128,37,5},//sépia
  {110,50,30}//blanc faible
};

byte Value[REGISTERSIZE];
byte newValue[REGISTERSIZE];

int fadeInterval[DECINPIN];
long unsigned initTimeChange[DECINPIN];
int steps[DECINPIN];
byte outpin[6] = {9, 3, 6, 5, A7, 4};

byte inpin[3] = {2, 7, 8};

byte inpinanalog[3] = {A6, A1, A0};

#define NGYRO 4
byte gyropin[NGYRO] = {A2, A3, A4, A5};
long unsigned lastGyroUpdate;
int gyroStep;
byte gyroAllOnTrick;


long unsigned lastStrob;
byte strobStep;
long unsigned lastGyroStrob;
byte strobGyroStep;
long unsigned last10wStrob;
byte strob10wStep;

long unsigned lastCheckInput;
int checkInputPeriod;

long unsigned lastCheckTension;
long checkTensionPeriod;

long interruptTimeOn;
int timeOutInterrupt=1500;

boolean interruptPending(){
  if(Value[INTERRUPT] == 0)return false;
  return true;
}


void freeInterrupt(){
  newValue[INTERRUPT] = 0;
  Value[INTERRUPT] = newValue[INTERRUPT];
  digitalWrite(outpin[INTERRUPT], LOW);
}


void setup (void) {
  Serial.begin(115200);
  clearRegister();
  initpin();
  initSPIslave();
  Serial.println("hello");
  newValue[UBATT] = 1;
  newValue[BOARDMODE] = BOARDMODE_AUTOLIGHT;
  Value[BOARDMODE] = newValue[BOARDMODE];
  checkInputPeriod = 50;
  checkTensionPeriod = 60000;
}

void setInterrupt(byte interrupt){
  newValue[INTERRUPT] = interrupt;
  Value[INTERRUPT] = newValue[INTERRUPT];
  printf_P(PSTR("interupt %u\n"),Value[INTERRUPT]);
  interruptTimeOn = millis();
  digitalWrite(outpin[INTERRUPT], HIGH);
  SPDR = interrupt;
}

void poweroff(){
  // disable ADC
  ADCSRA = 0;
  set_sleep_mode (SLEEP_MODE_PWR_DOWN);
  sleep_enable();
  while(1)sleep_cpu ();
}

void initpin() {
  byte i = 0;
  for (i = 0; i < DECINPIN; i++) {
    pinMode(outpin[i], OUTPUT);
    initTimeChange[i] = 0;
    fadeInterval[i] = 0;
    steps[i] = 0;
    updateValue(i);
  }

  for (i = DECINPIN; i < DECALALOGPIN; i++) {
    pinMode(inpin[i - DECINPIN], INPUT);
  }

  for (i = 0; i < NGYRO; i++) {
    pinMode(gyropin[i], OUTPUT);
    digitalWrite(gyropin[i], LOW);
  }
  gyroStep = 0;
  strobStep = 0;
  strobGyroStep = 0;
  strob10wStep = 0;
}

void clearRegister() {
  for (byte i = 0; i < REGISTERSIZE; i++) {
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
  }
  else {
    //valeur
    if (command == WRITECOMMANDVALUE) {
      Serial.print  ("wv ");
      Serial.println (adress);
      Serial.print  (" - ");
      Serial.println (c);
      if(adress<REGISTERSIZE)newValue[adress] = c;
      if (adress < DECINPIN)fadeInterval[adress] = 0;
      command = 1;
      SPDR = 0;
      return;
    }
    //fade
    if (command == WRITECOMMANDFADE) {
      Serial.println ("wf");
      if (adress < DECINPIN) {
        int v = Value[adress];
        v = abs(v - newValue[adress]);
        float f = c;
        f = f / v * 1000;
        //Serial.println(f, 2);
        fadeInterval[adress] = (int)f;
        initTimeChange[adress] = millis();
        steps[adress] = 0;
        command = 1;
      }
      SPDR = 0;
      return;
    }

  }
  //renvoie la valeur enregistree
  if (command == READCOMMAND) {
    if(adress<REGISTERSIZE)SPDR = Value[adress];
    command = 1;
    Serial.print("r ");
    Serial.println (Value[adress],DEC);
    if (inputRange(adress) || adress==UBATT) {
      freeInterrupt();
    }

  }


}  // end of interrupt service routine (ISR) SPI_STC_vect


//boucle principale

void loop (void) {

  // if SPI not active, clear current command
  if (digitalRead (SS) == HIGH) command = 0;

  //verification changement de valeur
  if (command == 0) {
    for (byte i = 0; i < REGISTERSIZE; i++) {
      if (Value[i] != newValue[i]) {
        if (outputRange(i)) {updateValue(i);} //cas valeur led RVB et led10w (fade possible)
        else if (inputRange(i)) {updateInput(i);}
        else {
          //cas autre valeur (sans fade)
          Value[i] = newValue[i];
          /*Serial.print(millis(), DEC);
          Serial.print(" new ");
          Serial.print(i, DEC);
          Serial.print(" - v ");
          Serial.println(Value[i], DEC);*/


          //cas particulier
          if (i == GYROMODE) gyroUpdate();
          if (i == LEDRVBSTROBSPEED)lastStrob = millis();
          if (i == LEDRVBSTROBSPEED && Value[i] == 0) strobRoutine(1);
          if (i == LED10W1STROBSPEED)last10wStrob = millis();
          if (i == LED10W1STROBSPEED && Value[i] == 0) strob10wRoutine(1);
          if (i == POWERDOWN && Value[i] == 100) poweroff();
          if (i == GYROSTROBSPEED) {
            newValue[GYROMODE] = 0;
            Value[GYROMODE] = 0;
            lastGyroStrob = millis();
          }
          if (i == GYROSTROBSPEED && Value[i] == 0)   gyroUpdate();
          
        }

      }
    }
  }

  if (Value[UBATT] == 0) readTensionBatt();
  if (Value[GYROMODE] > GYROALLOFF) gyroRoutine();
  if (Value[LEDRVBSTROBSPEED] > 0) strobRoutine(0);
  if (Value[LED10W1STROBSPEED] > 0) strob10wRoutine(0);
  if (Value[GYROSTROBSPEED] > 0) strobGyroRoutine();

  checkInput();
  checkTension();
  if (interruptPending() && millis()>interruptTimeOn+timeOutInterrupt) {
    printf_P(PSTR("warning interrupt read fail\n"));
    freeInterrupt();
  }

}  // end of loop

bool inputRange(byte i){
  if(i>= DECINPIN && i < DECALALOGPIN + 1) return true;
  return false;
}

bool outputRange(byte i){
  if(i<DECINPIN-1) return true;
  return false;
}


//fonction pour generer une interuption sur le rpi
void updateInput(byte i) {
  if (!interruptPending()) {
    Value[i] = newValue[i];
    setInterrupt(i);
  }
}


void checkInput() {
  if (millis() > lastCheckInput + checkInputPeriod) {
    //boutons
    for (byte i = 0; i < DECALALOGPIN - DECINPIN; i++) {
      byte buttonState = 1 - digitalRead(inpin[i]);
      //check for manual light
      if (Value[BOARDMODE]==BOARDMODE_MANUALLIGHT){
        if(DECINPIN + i == PUSH1 && newValue[DECINPIN + i] == 0 && buttonState ==1){
          manuallightPos=(manuallightPos+1)%manuallightPosStep;
          newValue[LEDRVALUE]=manuallightConduite[manuallightPos][0];
          newValue[LEDVVALUE]=manuallightConduite[manuallightPos][1];
          newValue[LEDBVALUE]=manuallightConduite[manuallightPos][2];
        }
        if(DECINPIN + i == PUSH2 && newValue[DECINPIN + i] == 0 && buttonState ==1){
          manuallightPosGyro=(manuallightPosGyro+1)%manuallightPosGyroStep;
          if(manuallightPosGyro==0) newValue[GYROMODE]=GYROALLOFF;
          else {newValue[GYROMODE]=GYROLEFT;
            newValue[GYROSPEED]=1;}
          
        }
        if(DECINPIN + i == PUSH3 && newValue[DECINPIN + i] == 0 && buttonState ==1){
          manuallightPos10w=(manuallightPos10w+1)%manuallightPos10wStep;
          newValue[LED10W1VALUE]=manuallightPos10w*255;
        }
      }
      //get value of button to raise interrupt
      newValue[DECINPIN + i] = buttonState;
    }
    if (Value[BOARDCHECKFLOAT] == 1) newValue[FLOAT] = map(analogRead(inpinanalog[FLOAT - DECALALOGPIN]), 0, 1024, 0, 255);
    lastCheckInput = millis();
  }
}

void checkTension() {
  if ((millis() > lastCheckTension + checkTensionPeriod)  && !interruptPending()) {
    Serial.println("interrupt tension");
    setInterrupt(UBATT);
    lastCheckTension= millis();
  }
}




//courbe pour adapter la luminosite

byte lightfunc(byte v) {
  long l = (long)v * (long)v;
  //Serial.println(l, DEC);
  float f = l;
  f = f / 255;
  //Serial.println(f, 2);
  return (byte)f;
}

//gestion du changement de valeur sortie LED RVB et led 10W1

void updateValue(byte i) {
  //because 10W2 do not work in current version
  if (fadeInterval[i] == 0) {
    Value[i] = newValue[i];
    /*Serial.print(millis(), DEC);
    Serial.print(" new ");
    Serial.print(i, DEC);
    Serial.print(" - v ");
    Serial.println(Value[i], DEC);*/
    analogWrite(outpin[i], lightfunc(Value[i]));
  } else if (outputRange(i)  && millis() > (initTimeChange[i] + (long)steps[i] * (long)fadeInterval[i])) {

    if (newValue[i] > Value[i])Value[i]++; else Value[i]--;
    steps[i]++;
    analogWrite(outpin[i], lightfunc(Value[i]));
    /*Serial.print(millis(), DEC);
    Serial.print(" new ");
    Serial.print(i, DEC);
    Serial.print(" - v ");
    Serial.print(Value[i], DEC);
    Serial.print(" - fi ");
    Serial.print(fadeInterval[i], DEC);
    Serial.print(" s ");
    Serial.println(steps[i], DEC);*/
  }
}

//gestion des gyro (clignotement)

void gyroRoutine() {
  if (Value[GYROMODE] == GYROALLON) {
    gyroAllOnTrick=(gyroAllOnTrick+1)%2;
      for (byte i = 0; i < NGYRO; i++) {
        if(gyroAllOnTrick==1) digitalWrite(gyropin[i], HIGH);
        else digitalWrite(gyropin[i], LOW);
    }
  }else{
  if (millis() > lastGyroUpdate + (100L * Value[GYROSPEED])) {
    //Serial.print("gyr ");
    //Serial.println(gyroStep,DEC);
    digitalWrite(gyropin[gyroStep], LOW);
    if (Value[GYROMODE] == 2)gyroStep = (gyroStep + 1) % NGYRO;
    if (Value[GYROMODE] == 3)gyroStep = (gyroStep + NGYRO - 1) % NGYRO;
    digitalWrite(gyropin[gyroStep], HIGH);
    lastGyroUpdate += 100L * Value[GYROSPEED];
  }
  }
}

//stob sur la sortie LED RVB

void strobRoutine(byte force) {
  if (millis() > lastStrob + (10L * Value[LEDRVBSTROBSPEED]*20*(1-strobStep)) || force) {
    strobStep = (strobStep + 1) % 2;
    if (force)strobStep = 1;
    for (byte i = 0; i < 3; i++) {
      analogWrite(outpin[i], lightfunc(Value[i])*strobStep);
    }
    lastStrob += 10L * Value[LEDRVBSTROBSPEED];
  }
}

//stob sur la sortie LED10W1

void strob10wRoutine(byte force) {
  if (millis() > last10wStrob + (10L * Value[LED10W1STROBSPEED]*20L*(1-strob10wStep)) || force) {
    strob10wStep = (strob10wStep + 1) % 2;
    if (force)strob10wStep = 1;
    analogWrite(outpin[LED10W1VALUE], lightfunc(Value[LED10W1VALUE])*strob10wStep);
    last10wStrob += 10L * Value[LED10W1STROBSPEED];
  }
}

//gestion des gyro (strob)

void strobGyroRoutine() {
    if (millis() > lastGyroStrob + (10L * Value[GYROSTROBSPEED]*20L*(1-strobGyroStep))) {
    strobGyroStep = (strobGyroStep + 1) % 2;
    for (byte i = 0; i < NGYRO; i++) {
      digitalWrite(gyropin[i], strobGyroStep);
    }
    lastGyroStrob += 10L * Value[GYROSTROBSPEED];
  }
}



void gyroUpdate() {
  if (Value[GYROMODE] == GYROALLOFF) {
    for (byte i = 0; i < NGYRO; i++) {
      digitalWrite(gyropin[i], LOW);
    }
    return;
  }
  if (Value[GYROMODE] == GYROALLON) {
    gyroAllOnTrick=0;
  }
  if (Value[GYROMODE] > GYROALLOFF) lastGyroUpdate = millis();
}






void readTensionBatt() {
  int batt = analogRead(inpinanalog[UBATT - DECALALOGPIN]);
  long voltage;
  //if (batt <= 438) voltage = (long)batt * 54 + 206;
  //else  voltage = (long)batt * 765 - 312500;
  voltage = (long)batt * 54 + 206;
  if(voltage>24600)voltage += (((long)batt)*732 - 329000);
  if (voltage<5000) voltage=5000;
  if (voltage>30000) voltage=30000;
  newValue[UBATT] = (byte) ((voltage - 5000) / 100);
  Value[UBATT] = newValue[UBATT];
  Serial.print("bat ");
  Serial.print(batt, DEC);
  Serial.print(" - ");
  Serial.print(voltage, DEC);
  Serial.print(" - ");
  Serial.println(Value[UBATT], DEC);
}



