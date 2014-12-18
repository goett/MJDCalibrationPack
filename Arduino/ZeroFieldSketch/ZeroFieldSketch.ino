/* Purpose: Hall Probe Messaging to ORCA
*  Operating Conditions: -Arduino UNO R3 connected via serial port to host computer running ORCA
*                        -Hall Probe Circuit R2 connected to ADC lines of UNO
*  Output:
*  modified from default CmdMessenger sketch: https://github.com/dreamcat4/cmdmessenger
*  Johnny Goett - goett@lanl.gov
*  31 Oct 2012 - Halloween
*  1  Nov 2012 - experiment with controlConstants.
*  1  Feb 2013 - integrate into calibration system prototype: recalibrate fields etc...
*  2  Jul 2013 - Testing with final calibration system prototype.
*/

#include<CmdMessenger.h>
#include <Streaming.h>

int led = 13;
int pos0 = 2;
int pos1 = 4;

void setup() 
{
  Serial.begin(115200); // Arduino Uno, Mega, with AT8u2 USB
  pinMode(led, OUTPUT);
  digitalWrite(led, LOW);
}

void loop() 
{
  digitalWrite(led, LOW);
  DoMeasurement();
}

boolean         lastPinState[14];
boolean         pinState[14];
unsigned long   lastDebounceTime[14];
unsigned long   debounceDelay = 50;

//Hall Probe Circuit Code, modified from sketch_oct23b

#define NOFIELD0 383L    // Analog output with no applied field, calibrate this
#define NOFIELD2 387L
#define NOFIELD4 388L

#define TOFIELDmG 3756L  // For A1302: 1.3mV = 1Gauss, and 1024 analog steps = 5V, so 1 step = 3756mG

int lastPos = 0;
int currPos = 0;

int last0 = 0;
int last2 = 0;
int last4 = 0;

void DoMeasurement()
{
  //default is, field is off
  digitalWrite(led, LOW);
// measure magnetic field
  int raw0 = analogRead(0);   // Range : 0..1024
  int raw2 = analogRead(2);   // Range : 0..1024
  int raw4 = analogRead(4);   // Range : 0..1024

  //  Uncomment this to get a raw reading for calibration of no-field point
  if( abs(raw0-last0)>50 || abs(raw2-last2)>50 || abs(raw4-last4)>50)
  {
    Serial.print("Raw reading 0: ");
    Serial.println(raw0);
    Serial.print("Raw reading 2: ");
    Serial.println(raw2);
    Serial.print("Raw reading 4: ");
    Serial.println(raw4);
    last0 = raw0;
    last2 = raw2;
    last4 = raw4;
    Serial.println("//////////////////");
  }
  
  

  long compensated0 = raw0 - NOFIELD0;                 // adjust relative to no applied field 
  long gauss0 = compensated0 * TOFIELDmG / 1000;   // adjust scale to Gauss
  
  long compensated2 = raw2 - NOFIELD2;                 // adjust relative to no applied field 
  long gauss2 = compensated2 * TOFIELDmG / 1000;   // adjust scale to Gauss
  
  long compensated4 = raw4 - NOFIELD4;                 // adjust relative to no applied field 
  long gauss4 = compensated4 * TOFIELDmG / 1000;   // adjust scale to Gauss
  
  //Field state for garaged source
  if((gauss0>10) && abs(gauss2-gauss4)<10){
    digitalWrite(led, HIGH);
    currPos=1;
  }
  //Field State for deployed source
  else if((gauss2>10) && abs(gauss0-gauss4)<10){
    digitalWrite(led, HIGH);
    currPos=2;
  }
  //Field State for intermediate position 1
  else if((gauss4>10) && abs(gauss0-gauss2)<10){
    digitalWrite(led, HIGH);
    currPos=3;
  }
  //Field State for intermediate position 2
  else if((gauss0==1000) && (gauss2==1000)){
    digitalWrite(led, HIGH);
    currPos=4;
  }
  //Field State for source in transit
  else if((gauss0) && (gauss2==1000)){
    digitalWrite(led, LOW);
    currPos=5;
  }
  
  if(!(currPos==lastPos)){
    /*
    Serial << "21" << "," << "0" << "," << "1" << "\n\r";
    Serial << "21" << "," << "1" << "," << currPos << "\n\r";
    Serial << "21" << "," << "0" << "," << "0" << "\n\r";
    */
    Serial.println("Position Changed");
  }
  lastPos=currPos;
 
 //example:  kCustomValueChanged,channelNumber,value;
 //Serial << kCustomValueChanged << "," << 0 << "," << 123 << "\n\r";

}
