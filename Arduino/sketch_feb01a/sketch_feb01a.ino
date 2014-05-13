/* Purpose: Hall Probe Messaging to ORCA
*  Operating Conditions: -Arduino UNO R3 connected via serial port to host computer running ORCA
*                        -Hall Probe Circuit R2 connected to ADC lines of UNO
*  Output:
*  modified from default CmdMessenger sketch: https://github.com/dreamcat4/cmdmessenger
*  Johnny Goett - goett@lanl.gov
*  31 Oct 2012 - Halloween
*  1  Nov 2012 - experiment with controlConstants.
*  1  Feb 2013 - integrate into calibration system prototype: recalibrate fields etc...
*/

#include <CmdMessenger.h>
#include <Streaming.h>

char field_separator      = ',';
char command_separator    = ';';
unsigned short inputMask  = 0x0; 
unsigned short oldInputs  = 0x0;
unsigned short controlValue[10]    = {0,0,0,0,0,0,0,0,0,0};

// Attach a new CmdMessenger object to the default Serial port
CmdMessenger cmdMessenger = CmdMessenger(Serial, field_separator, command_separator);

// ------------------ C M D  L I S T I N G ( T X / R X ) ---------------------
//Commands from ORCA (never sent unsolicited)
short kCmdVerison			= 1;  //1;
short kCmdReadAdcs			= 2;  //2;             --read all adcs
short kCmdReadInputs		= 3;  //3,mask;        --read input pins using mask
short kCmdWriteAnalog		= 4;  //4,pin,value;   --set pin pwm to value
short kCmdWriteOutput		= 5;  //5,pin,value;   --set output pin to value
short kCmdWriteOutputs		= 6;  //6,mask;        --set outputs based on mask
short kCmdSetControlValue	= 7;  //7,chan,value;  --set control value. chan 0-9. value is unsigned short

//Messages which can be sent unsolicited to ORCA.
short kInputsChanged		= 20; //20,i0,i1,i2,...i13;
short kCustomValueChanged   = 21; //21,chan,value
short kAdcValueChanged		= 22; //22,chan,value
short kUnKnownCmd			= 99;

float kSketchVersion = 1.1; //change whenever command formats change

// ------------------ C A L L B A C K  M E T H O D S -------------------------
void readAnalogValues()
{
    Serial<<2;
    for(char i=0;i<6;i++) Serial << "," << analogRead(i);
    Serial<< "\n\r";
}

void readInputPins()
{
    inputMask = cmdMessenger.readInt();
    Serial << kCmdReadInputs;
    for (char i=0;i<14;i++) {
      if(inputMask & (1<<i)) {
        if(i>=2){
           pinMode(i, INPUT_PULLUP);
           Serial << "," << digitalRead(i);
        }
        else Serial<<",0"; //return 0 for the serial lines
      }
      else   Serial<<",0";
    }
    Serial<<"\n\r";
}

void writeOutputPin()
{
      char pin   = cmdMessenger.readInt();  
      char state = cmdMessenger.readInt();
      if(pin>=2 && (~inputMask & (1<<pin))){
         pinMode(pin,OUTPUT);  
         if( state)  digitalWrite(pin,HIGH);
         else        digitalWrite(pin,LOW);
      }
      Serial<< kCmdWriteOutput << "," << pin << "," << state << "\n\r";
}
  

void writeOutputs()
{
    char pin;
    short outputTypeMask  = cmdMessenger.readInt() & ~inputMask; //don't write inputs
    short writeMask       = cmdMessenger.readInt() & ~inputMask;  
    if(outputTypeMask){
      for(pin=2;pin<14;pin++){
        if(outputTypeMask & (1<<pin)){
           pinMode(pin,OUTPUT);
           if( writeMask & (1<<pin))  digitalWrite(pin,HIGH);
           else                       digitalWrite(pin,LOW);
        }
      }
    }
    else writeMask = 0;
    //echo the command back
    Serial << kCmdWriteOutputs << "," << outputTypeMask << "," << writeMask << "\n\r";
}

void writeAnalog()
{
     char pin   = cmdMessenger.readInt(); 
     char state = cmdMessenger.readInt();
      if(pin>=2 && (~inputMask & (1<<pin))){
        pinMode(pin, OUTPUT);
        analogWrite(pin, state); //Sets the PWM value of the pin 
      }
      //echo the command back
      Serial<< kCmdWriteAnalog << "," << pin << "," << state << "\n\r";
}

void setControlValue()
{
	//users can use this value in their custom code as needed.
    short chan  = cmdMessenger.readInt();
    unsigned short value = cmdMessenger.readInt(); 
    if(chan>=0 && chan<10){
		controlValue[chan] = value;
    }
    //echo the command back
    Serial << kCmdSetControlValue << "," << chan << "," << value << "\n\r";
}


void sketchVersion()  { Serial << kCmdVerison<<","<< kSketchVersion << "\n\r";   }
void unKnownCmd()     { Serial << kUnKnownCmd << "\n\r";  }

// ------------------ E N D  C A L L B A C K  M E T H O D S ------------------

int led = 13;
int pos0 = 2;
int pos1 = 4;

void setup() 
{
  Serial.begin(115200); // Arduino Uno, Mega, with AT8u2 USB
  pinMode(led, OUTPUT);
  digitalWrite(led, LOW);

  cmdMessenger.print_LF_CR();
  cmdMessenger.attach(kCmdVerison,     sketchVersion);
  cmdMessenger.attach(kCmdReadAdcs,    readAnalogValues);
  cmdMessenger.attach(kCmdReadInputs,  readInputPins);
  cmdMessenger.attach(kCmdWriteAnalog, writeAnalog);
  cmdMessenger.attach(kCmdWriteOutput, writeOutputPin);
  cmdMessenger.attach(kCmdWriteOutputs,writeOutputs);
  cmdMessenger.attach(kCmdSetControlValue,setControlValue);

  cmdMessenger.attach(unKnownCmd);
}

void loop() 
{
  digitalWrite(led, LOW);
  cmdMessenger.feedinSerialData(); //process incoming commands
  //scanInputsForChange();
  DoMeasurement();
}

/*void scanInputsForChange()
{
  if(inputMask){
      unsigned short inputs = 0;
      if(inputMask){
        for (char i=2;i<14;i++) {
          if(inputMask & (1<<i)){
            inputs |= ((unsigned short)debouncedDigitalRead(i) << i);
          }
        }
        if(inputs != oldInputs){
          oldInputs = inputs;
          Serial << kInputsChanged << "," << inputs <<  "\n\r";
        }
      }
  }
}
*/

boolean         lastPinState[14];
boolean         pinState[14];
unsigned long   lastDebounceTime[14];
unsigned long   debounceDelay = 50;

/*
boolean debouncedDigitalRead(int aPin)
{
  boolean currentValue = digitalRead(aPin);
  if (currentValue != lastPinState[aPin]) lastDebounceTime[aPin] = millis();
  if ((millis() - lastDebounceTime[aPin]) > debounceDelay) pinState[aPin] = currentValue;
  lastPinState[aPin] = currentValue;
  return pinState[aPin];
}
*/

//Hall Probe Circuit Code, modified from sketch_oct23b

#define NOFIELD0 390L    // Analog output with no applied field, calibrate this
#define NOFIELD2 362L

#define TOFIELDmG 3756L  // For A1302: 1.3mV = 1Gauss, and 1024 analog steps = 5V, so 1 step = 3756mG

int lastPos = 0;
int currPos = 0;

void DoMeasurement()
{
  //default is, field is off
  digitalWrite(led, LOW);
// measure magnetic field
  int raw0 = analogRead(0);   // Range : 0..1024
  int raw2 = analogRead(2);   // Range : 0..1024

//  Uncomment this to get a raw reading for calibration of no-field point
//Serial.print("Raw reading 0: ");
//Serial.println(raw0);
//Serial.print("Raw reading 2: ");
//Serial.println(raw2);

  long compensated0 = raw0 - NOFIELD0;                 // adjust relative to no applied field 
  long gauss0 = compensated0 * TOFIELDmG / 1000;   // adjust scale to Gauss
  
  long compensated2 = raw2 - NOFIELD2;                 // adjust relative to no applied field 
  long gauss2 = compensated2 * TOFIELDmG / 1000;   // adjust scale to Gauss
  
Serial.print("Gauss reading 0: ");
Serial.println(gauss0);
Serial.print("Gauss reading 2: ");
Serial.println(gauss2);
  
  if((gauss0<10) && (gauss2<-300)){
    digitalWrite(led, HIGH);
    currPos=1;
  }
  else if((gauss0<-270) && (gauss2<-290)){
    digitalWrite(led, HIGH);
    currPos=2;
  }
  else{
    digitalWrite(led, LOW);
    currPos=0;
  }
  if(!(currPos==lastPos)){
    Serial << kCustomValueChanged << "," << 0 << "," << 1 << "\n\r";
    Serial << kCustomValueChanged << "," << 1 << "," << currPos << "\n\r";
    Serial << kCustomValueChanged << "," << 0 << "," << 0 << "\n\r";
  }
  lastPos=currPos;
 
 //example:  kCustomValueChanged,channelNumber,value;
 //Serial << kCustomValueChanged << "," << 0 << "," << 123 << "\n\r";

}
