/* Purpose: Hall Switch Messaging to ORCA
*  Operating Conditions: -Arduino UNO R3 connected via serial port to host computer running ORCA
*                        -Hall Probe Circuit R2 connected to pin3 of UNO
*  Output: Serial printing of hall switch state
*  Johnny Goett - goett@lanl.gov
*  2 Jan 2015 - initial migration from calibration code
*/

//#include<CmdMessenger.h>
#include <Streaming.h>

int led = 13;
int inPinA = 3;
int inPinB = 6;
int inPinC = 9;
int valA = 0;
int valB = 0;
int valC = 0;
int laststate = 0;
int switchcount = 0;
long mcount;

void setup() 
{
  Serial.begin(115200); // Arduino Uno, Mega, with AT8u2 USB
  pinMode(led, OUTPUT);
  pinMode(inPinA, INPUT_PULLUP);
  pinMode(inPinB, INPUT_PULLUP);
  pinMode(inPinC, INPUT_PULLUP);
  digitalWrite(led, LOW);
  Serial.println("Setup complete");
}

void loop() 
{
  DoMeasurement();
}

//Hall Probe Circuit Code, modified from sketch_oct23b

void DoMeasurement()
{
  
// measure magnetic field
  valA = digitalRead(3);
  valB = digitalRead(6);
  valC = digitalRead(9);
  
  if(valA == LOW){
    Serial.print(valA);
    Serial.print('\t');
    Serial.print(valB);
    Serial.print('\t');
    Serial.print(valC);
    Serial.print('\n');
  }
 
  
}
