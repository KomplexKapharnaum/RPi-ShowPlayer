#include <avr/pgmspace.h>
int state = MCUSR;
#include "pins_arduino.h"
#include <avr/sleep.h>
#include "printf.h"


//For lighter program, if undef M_SERIAL_DEBUG, do not include debug code line.
#define M_SERIAL_DEBUG
//#undef M_SERIAL_DEBUG

#ifdef M_SERIAL_DEBUG
#define M_IF_SERIAL_DEBUG(x) ({x;})
#else
#define M_IF_SERIAL_DEBUG(x)
#endif


// what to do with incoming data
volatile byte command = 0;
volatile byte adress = 0;
volatile byte value = 0;
volatile byte fadeValue = 0;
volatile byte post= 0;




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

byte manuallightPos=0;
byte manuallightPosGyro=0;
byte manuallightPos10w=0;
byte manuallightPosStep=10;
byte manuallightPosGyroStep=2;
byte manuallightPos10wStep=2;


byte manuallightConduite[10][3]={
  {0,0,0},
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
byte inpinOffValue[3] = {0, 0, 0};

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
long timeOutInterrupt=1500;

boolean interruptPending(){
  if(Value[INTERRUPT] == 0)return false;
  return true;
}


void freeInterrupt(){
  M_IF_SERIAL_DEBUG(printf_P(PSTR("free interrupt\n")));
  delay(1);
  newValue[INTERRUPT] = 0;
  Value[INTERRUPT] = newValue[INTERRUPT];
  digitalWrite(outpin[INTERRUPT], LOW);
}

#define BOARDMODE_MANUALLIGHT 0
#define BOARDMODE_AUTOLIGHT 1

void setup (void) {
  Serial.begin(115200);
  Serial.println("hello");
  printf_begin();
  M_IF_SERIAL_DEBUG(
                    if(state & (1<<PORF )) printf_P(PSTR("Power-on reset.\n"));
                    if(state & (1<<EXTRF)) printf_P(PSTR("External reset!\n"));
                    if(state & (1<<BORF )) printf_P(PSTR("Brownout reset!\n"));
                    if(state & (1<<WDRF )) printf_P(PSTR("Watchdog reset!\n"));
                    );
  clearRegister();
  initpin();
  initSPIslave();
  newValue[UBATT] = 1;
  newValue[BOARDMODE] = BOARDMODE_MANUALLIGHT;
  Value[BOARDMODE] = newValue[BOARDMODE];
  checkInputPeriod = 50;
  checkTensionPeriod = 60000;
}



void setInterrupt(byte interrupt){
  newValue[INTERRUPT] = interrupt;
  Value[INTERRUPT] = newValue[INTERRUPT];
  M_IF_SERIAL_DEBUG(printf_P(PSTR("interupt %u\n"),Value[INTERRUPT]));
  interruptTimeOn = millis();
  digitalWrite(outpin[INTERRUPT], HIGH);
  SPDR = interrupt;
}

void poweroff(){
  M_IF_SERIAL_DEBUG(printf_P(PSTR("%lu - off output\n"),millis()));
  for (byte i=0; i<DECINPIN; i++) {
    newValue[i]=0;
    fadeInterval[i]=0;
    updateValue(i);
  }
  if(Value[BOARDMODE]!=BOARDMODE_MANUALLIGHT){
    M_IF_SERIAL_DEBUG(printf_P(PSTR("%lu - real poweroff\n"),millis()));
    delay(10);
    //disable interrupt
    cli();
    // disable ADC
    ADCSRA = 0;
    set_sleep_mode (SLEEP_MODE_PWR_DOWN);
    sleep_enable();
    while(1)sleep_cpu ();
  }
}

void initpin() {
  M_IF_SERIAL_DEBUG(printf_P(PSTR("%lu - init pinmode\n"),millis()));
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
    inpinOffValue[i - DECINPIN] = digitalRead(inpin[i - DECINPIN]);
    M_IF_SERIAL_DEBUG(printf_P(PSTR("off Value push%u = %u\n"),i - DECINPIN,inpinOffValue[i - DECINPIN]));
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
  M_IF_SERIAL_DEBUG(printf_P(PSTR("%lu - init register\n"),millis()));
  for (byte i = 0; i < REGISTERSIZE; i++) {
    Value[i] = 0;
    newValue[i] = 0;
    if(i<DECINPIN){
      fadeInterval[i]=0;
      initTimeChange[i]=0;
      steps[i]=0;
    }
  }
}

void initSPIslave() {
  M_IF_SERIAL_DEBUG(printf_P(PSTR("%lu - init SPI slave\n"),millis()));
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
  
  if (command < 10) {
    adress = c & ~COMMANDMASK;
    command = c & COMMANDMASK;
  }
  else {
    //valeur
    if (command == WRITECOMMANDVALUE) {
      if(adress<REGISTERSIZE)value = c;
      command = 1;
      post=1;
      SPDR = 0;
      return;
    }
    //fade
    if (command == WRITECOMMANDFADE) {
      if (adress < DECINPIN) {
        fadeValue=c;
        command = 1;
        post=2;
      }
      SPDR = 0;
      return;
    }
  }
  //renvoie la valeur enregistree
  if (command == READCOMMAND) {
    if(adress<REGISTERSIZE)SPDR = Value[adress];
    command = 1;
    post=3;
  }
}  // end of interrupt service routine (ISR) SPI_STC_vect


void checkEndSPI(){
  if (digitalRead (SS) == HIGH && command!=0){
    
    if (post==1) {
      newValue[adress]=value;
      if (adress<DECINPIN)fadeInterval[adress] = 0;
      M_IF_SERIAL_DEBUG(printf_P(PSTR("%lu - write %u = %u\n"),millis(),adress,value));
    }
    
    if(post==2){
      newValue[adress]=value;
      int v = Value[adress];
      v = abs(v - newValue[adress]);
      float f = fadeValue;
      f = f / v * 1000;
      fadeInterval[adress] = (int)f;
      initTimeChange[adress] = millis();
      steps[adress] = 0;
      M_IF_SERIAL_DEBUG(printf_P(PSTR("%lu - write %u = %u with fade = %u\n"),millis(),adress,value,fadeValue));
    }
    
    if(post==3){
      M_IF_SERIAL_DEBUG(printf_P(PSTR("%lu - read %u = %u\n"),millis(),adress,Value[adress]));
      if (inputRange(adress) || adress == UBATT) {
        freeInterrupt();
      }
    }
    
    post=0;
    value=0;
    fadeValue=0;
    adress=0;
    command=0;
  }
}

//boucle principale

void loop (void) {
  
  // if SPI not active, clear current command
  checkEndSPI();
  
  //verification changement de valeur
  if (command == 0) {
    for (byte i = 0; i < REGISTERSIZE; i++) {
      if (Value[i] != newValue[i]) {
        if (outputRange(i)) {updateValue(i);} //cas valeur led RVB et led10w (fade possible)
        else if (inputRange(i)) {updateInput(i);}
        else {
          //cas autre valeur (sans fade)
          Value[i] = newValue[i];
          M_IF_SERIAL_DEBUG(printf_P(PSTR("%lu - new other %u = %u\n"),millis(),i,Value[i]));
          
          
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
    //end loop
  }
  
  if (Value[UBATT] == 0) readTensionBatt();
  if (Value[GYROMODE] > GYROALLOFF) gyroRoutine();
  if (Value[LEDRVBSTROBSPEED] > 0) strobRoutine(0);
  if (Value[LED10W1STROBSPEED] > 0) strob10wRoutine(0);
  if (Value[GYROSTROBSPEED] > 0) strobGyroRoutine();
  
  checkInput();
  checkTension();
  if (interruptPending() && millis()>interruptTimeOn+timeOutInterrupt) {
    M_IF_SERIAL_DEBUG(printf_P(PSTR("warning interrupt read fail => ")));;
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
    M_IF_SERIAL_DEBUG(printf_P(PSTR("%lu - new output %u = %u\n"),millis(),i,Value[i]));
    Value[i] = newValue[i];
    setInterrupt(i);
  }
}


void checkInput() {
  if (millis() > lastCheckInput + checkInputPeriod) {
    //boutons
    for (byte i = 0; i < DECALALOGPIN - DECINPIN; i++) {
      
      byte buttonState = digitalRead(inpin[i]);
      if (buttonState != inpinOffValue[i]) buttonState=1;
      else buttonState=0;
        //check for manual light
      if (Value[BOARDMODE]==BOARDMODE_MANUALLIGHT){
        if(DECINPIN + i == PUSH1 && newValue[DECINPIN + i] == 0 && buttonState == 1){
          M_IF_SERIAL_DEBUG(printf_P(PSTR("update manual RGB\n")));
          manuallightPos=(manuallightPos+1)%manuallightPosStep;
          newValue[LEDRVALUE]=manuallightConduite[manuallightPos][0];
          newValue[LEDVVALUE]=manuallightConduite[manuallightPos][1];
          newValue[LEDBVALUE]=manuallightConduite[manuallightPos][2];
        }
        if(DECINPIN + i == PUSH2 && newValue[DECINPIN + i] == 0 && buttonState == 1){
          M_IF_SERIAL_DEBUG(printf_P(PSTR("update manual gyro\n")));
          manuallightPosGyro=(manuallightPosGyro+1)%manuallightPosGyroStep;
          if(manuallightPosGyro==0) newValue[GYROMODE]=GYROALLOFF;
          else {newValue[GYROMODE]=GYROLEFT;
            newValue[GYROSPEED]=1;}
          
        }
        if(DECINPIN + i == PUSH3 && newValue[DECINPIN + i] == 0 && buttonState == 1){
          M_IF_SERIAL_DEBUG(printf_P(PSTR("update manual 10w \n")));
          manuallightPos10w=(manuallightPos10w+1)%manuallightPos10wStep;
          newValue[LED10W1VALUE]=manuallightPos10w*255;
        }
      }
      //get value of button to raise interrupt
      newValue[DECINPIN + i] = buttonState;
    }
    if (Value[BOARDCHECKFLOAT] == 1) {
      newValue[FLOAT] = map(analogRead(inpinanalog[FLOAT - DECALALOGPIN]), 0, 1024, 0, 255);
    }
    lastCheckInput = millis();
  }
}

void checkTension() {
  if ((millis() > lastCheckTension + checkTensionPeriod)  && !interruptPending()) {
    M_IF_SERIAL_DEBUG(printf_P(PSTR("loop check tension\n")));
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
    M_IF_SERIAL_DEBUG(printf_P(PSTR("%lu - new output %u = %u\n"),millis(),i,Value[i]));
    analogWrite(outpin[i], lightfunc(Value[i]));
  } else if (outputRange(i)  && millis() > (initTimeChange[i] + (long)steps[i] * (long)fadeInterval[i])) {
    
    if (newValue[i] > Value[i])Value[i]++; else Value[i]--;
    steps[i]++;
    analogWrite(outpin[i], lightfunc(Value[i]));
    M_IF_SERIAL_DEBUG(printf_P(PSTR("%lu - update output %u = %u -fade %u -step %u\n"),millis(),i,Value[i],fadeInterval[i],steps[i]));
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
      M_IF_SERIAL_DEBUG(printf_P(PSTR("update gyro step %u\n"),gyroStep));
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
      M_IF_SERIAL_DEBUG(printf_P(PSTR("update strob RVB step %u\n"),strobStep));
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
    M_IF_SERIAL_DEBUG(printf_P(PSTR("update strob 10W step %u\n"),strob10wStep));
    analogWrite(outpin[LED10W1VALUE], lightfunc(Value[LED10W1VALUE])*strob10wStep);
    last10wStrob += 10L * Value[LED10W1STROBSPEED];
  }
}

//gestion des gyro (strob)

void strobGyroRoutine() {
  if (millis() > lastGyroStrob + (10L * Value[GYROSTROBSPEED]*20L*(1-strobGyroStep))) {
    strobGyroStep = (strobGyroStep + 1) % 2;
    for (byte i = 0; i < NGYRO; i++) {
      M_IF_SERIAL_DEBUG(printf_P(PSTR("update strob gyro step %u\n"),strobGyroStep));
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
  voltage = (long)batt * 54 + 206;
  if(voltage>24600)voltage += (((long)batt)*732 - 329000);
  if (voltage<5000) voltage=5000;
  if (voltage>30000) voltage=30000;
  newValue[UBATT] = (byte) ((voltage - 5000) / 100);
  Value[UBATT] = newValue[UBATT];
  M_IF_SERIAL_DEBUG(printf_P(PSTR("batterie %u > %u 0.1V > reg = %u\n"),batt,voltage,Value[UBATT]));
}



