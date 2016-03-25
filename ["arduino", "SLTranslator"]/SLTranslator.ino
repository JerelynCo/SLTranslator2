/*
Sign Language Translator with Flex sensors, contact sensors, gyroscope, and accelerometer using Teensy 3.1 using Teensy 3.1.

Created by: Jerelyn Co
Started: 2 Oct 2015

i2c accelerometer and gyro assignment:
Gnd: GND
3.3V: VCC
A4: SDA
A5: SLC

Flex sensors pins assignment
Digital pins: 15, 16, 17, 20, 21

Contact sensors pins assignment
2, 3, 4, 5

Enter button pin
6

Space button pin
7

*/

#include <Wire.h>

// accelerometer variables
#define DEVICEACCEL (0x53) // Device address as specified in data sheet 
byte _buff[6];
char POWER_CTL = 0x2D;  //Power Control Register
char ACCEL_FORMAT = 0x31;
char ACCELX0 = 0x32; //X-Axis Data 0
char ACCELX1 = 0x33; //X-Axis Data 1
char ACCELY0 = 0x34; //Y-Axis Data 0
char ACCELY1 = 0x35; //Y-Axis Data 1
char ACCELZ0 = 0x36; //Z-Axis Data 0
char ACCELZ1 = 0x37; //Z-Axis Data 1

//gyroscope variables: https://github.com/sparkfun/ITG-3200_Breakout/blob/master/Firmware/ITG3200_Example/ITG3200_Example.ino
// Gyroscope ITG3200 
#define GYRO 0x68 //  when AD0 is connected to GND ,gyro address is 0x68.
//#define GYRO 0x69   when AD0 is connected to VCC ,gyro address is 0x69  
#define G_SMPLRT_DIV 0x15
#define G_DLPF_FS 0x16
#define G_INT_CFG 0x17
#define G_PWR_MGM 0x3E
#define G_TO_READ 8 // 2 bytes for each axis x, y, z

// offsets are chip specific. 
int g_offx = 120;
int g_offy = 20;
int g_offz = 93;
int hx, hy, hz;
byte addr;
int16_t gyro[4];

// flex sensors variables
const int FLEXPINS[] = {15, 16, 17, 20, 21};
const int FLEXPINSCOUNT = sizeof(FLEXPINS)/sizeof(FLEXPINS[0]);

// contact sensors variables
const int CONTPINS[] = {2, 3, 4, 5};
const int CONTPINSCOUNT = sizeof(CONTPINS)/sizeof(CONTPINS[0]);

// temp array variables for flex sensors calibration
float flexValues[FLEXPINSCOUNT];  // array for the flex readings
int sensorMin[FLEXPINSCOUNT] = {1023, 1023, 1023, 1023, 1023};     // minimum sensor value
int sensorMax[FLEXPINSCOUNT] = {0};      // maximum sensor value

// array for the flex voltage converted values
float flex[FLEXPINSCOUNT]; 

// contains current sensor value
int sensorValue;

// start of data collection?
bool dataCollectStart = false;

// add on constant vars
const int SAMPLE_SIZE = 25;
const int CHARCOUNT = 30; //Number of total characters to read. Includes space and enter
const char CHARACTERS[CHARCOUNT] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"; //_ = space, / = enter, - = rest

// Keyboard interface variables
const int ENTER_BUTTON_PIN = 6;
const int SPACE_BUTTON_PIN = 7;
int enterButtonState, spaceButtonState = 0;
int lastEnterButtonState, lastSpaceButtonState = 0;

// time recording
//unsigned long old_time;
//unsigned long new_time;

void setup() {
  Wire.begin();
  Serial.begin(9600);
  
  //Flex sensors setup
  calibrateFlexSensors();

  //Contact Sensors setup
  for(int i = 0; i < CONTPINSCOUNT; i++){
    pinMode(CONTPINS[i], INPUT_PULLUP);
  }

  pinMode(ENTER_BUTTON_PIN, INPUT_PULLUP);
  pinMode(SPACE_BUTTON_PIN, INPUT_PULLUP);
  
  //Accelerometer setup
  initAccel();

  //Gyroscope setup
  initGyro();

  testUser();
}

void loop() {
  if(dataCollectStart){
    dataCollection();
  }
  else{
    //new_time=millis();
    displayValues();
    keyboard();
    
    /*Serial.print("-----------------------\n");
    Serial.print("Time difference: ");
    Serial.print(new_time - old_time);
    Serial.println("\n-----------------------\n");
    old_time = new_time;*/
  }
  delay(50);
}

void testUser(){  
  char varied_letters [] = ".ZHG";
  int n_varied_letters = 4;
  String merged;
  for(int i = 0; i < n_varied_letters; i++){ // goes through 3 letters
    merged = "==> [Test] Perform in 3s: ";
    Serial.print (varied_letters[i]);
    Serial.println(merged);
    delay(5000);
    displayValues();
    Serial.println();    
  }
}

void keyboard(){
  enterButtonState = digitalRead(ENTER_BUTTON_PIN);
  spaceButtonState = digitalRead(SPACE_BUTTON_PIN);
  
  if(enterButtonState != lastEnterButtonState){
    if(enterButtonState == LOW){
      Serial.println("enter");
    } 
  }

  if(spaceButtonState != lastSpaceButtonState){
    if(spaceButtonState == LOW){
      Serial.println("space");
    }
  }
  delay(50);
  
  lastEnterButtonState = enterButtonState;
  lastSpaceButtonState = spaceButtonState;
}

void displayValues(){
  //Reading and converting of flex sensor values
  for(int thisPin = 0; thisPin < FLEXPINSCOUNT; thisPin++){
    Serial.print(analogRead(FLEXPINS[thisPin]) - sensorMin[thisPin]); // difference of reading and min value
    //Serial.print(analogRead(FLEXPINS[thisPin]));
    Serial.print(",");
  }
  //reading of contact sensor values
  for(int thisPin = 0; thisPin < CONTPINSCOUNT; thisPin++) {
    Serial.print(digitalRead(CONTPINS[thisPin]));
    Serial.print(",");
  }
  readAccel();  
  readGyro();
}

/****** FLEX SENSORS FUNCTIONS ******/

float toVoltage(int sensorValue){
  return sensorValue * (3.3 / 1023.0);
}

void calibrateFlexSensors(){
  pinMode(13, OUTPUT);

  // signal the start of calibration
  digitalWrite(13, HIGH);

  bool pass = true;

  while (1) {
    for(int i = 0; i < FLEXPINSCOUNT; i++){
      flexValues[i] = analogRead(FLEXPINS[i]);
      
      // record the maximum sensor value
      if(flexValues[i] > sensorMax[i]){
        sensorMax[i] = flexValues[i];
      }
      // record the minimum sensor value
      if(flexValues[i] <  sensorMin[i]){
        sensorMin[i] = flexValues[i];
      }

      if(flexValues[i] - sensorMin[i] > 20){
        pass *= false; // if one of the elements' diff is
        //greater than 20, then calibration repeats
      }
    }
    if(pass==true){
      break; // if not, calibration succeeds
    }
  }
  
  // signal the end of the calibration period
  digitalWrite(13, LOW); 
}

/****** ACCELEROMETER FUNCTIONS ******/

void initAccel() {
  writeTo(ACCEL_FORMAT, 0x01);
  writeTo(POWER_CTL, 0x08);
}

void readAccel() {
  uint8_t howManyBytesToRead = 6;
  readFrom( ACCELX0, howManyBytesToRead, _buff); //read the acceleration data from the ADXL345

  // each axis reading comes in 10 bit resolution, ie 2 bytes.  Least Significat Byte first!!
  // thus we are converting both bytes in to one int
  int16_t x = (((int)_buff[1]) << 8) | _buff[0];   
  int16_t y = (((int)_buff[3]) << 8) | _buff[2];
  int16_t z = (((int)_buff[5]) << 8) | _buff[4];

  Serial.print(x);
  Serial.print(",");
  Serial.print( y );
  Serial.print(",");
  Serial.print( z );
  Serial.print(",");
}

void writeTo(byte address, byte val) {
  Wire.beginTransmission(DEVICEACCEL); // start transmission to device
  Wire.write(address);             // send register address
  Wire.write(val);                 // send value to write
  Wire.endTransmission();         // end transmission
}

// Reads num bytes starting from address register on device in to _buff array
void readFrom(byte address, int num, byte _buff[]) {
  Wire.beginTransmission(DEVICEACCEL); // start transmission to device
  Wire.write(address);             // sends address to read from
  Wire.endTransmission();         // end transmission

  Wire.beginTransmission(DEVICEACCEL); // start transmission to device
  Wire.requestFrom(DEVICEACCEL, num);    // request 6 bytes from device

  int i = 0;
  while (Wire.available())        // device may send less than requested (abnormal)
  {
    _buff[i] = Wire.read();    // receive a byte
    i++;
  }
  Wire.endTransmission();         // end transmission
}

/****** GYROSCOPE FUNCTIONS ******/
void initGyro(){
 writeToGyro(GYRO, G_PWR_MGM, 0x00);
 writeToGyro(GYRO, G_SMPLRT_DIV, 0x07); // EB, 50, 80, 7F, DE, 23, 20, FF
 writeToGyro(GYRO, G_DLPF_FS, 0x1E); // +/- 2000 dgrs/sec, 1KHz, 1E, 19
 writeToGyro(GYRO, G_INT_CFG, 0x00);
}

void getGyroscopeData(int16_t * result){
 int regAddress = 0x1B;
 int x, y, z;
 byte buff[G_TO_READ];
 readFromGyro(GYRO, regAddress, G_TO_READ, buff); //read the gyro data from the ITG3200
 result[0] = ((buff[2] << 8) | buff[3]) + g_offx;
 result[1] = ((buff[4] << 8) | buff[5]) + g_offy;
 result[2] = ((buff[6] << 8) | buff[7]) + g_offz;
}

void readGyro(){
  getGyroscopeData(gyro);
  hx = gyro[0] / 14.375;
  hy = gyro[1] / 14.375;
  hz = gyro[2] / 14.375;
  Serial.print(hx);
  Serial.print(",");
  Serial.print(hy);
  Serial.print(",");
  if(dataCollectStart == false){
    Serial.println(hz);
  }
  else{
    Serial.print(hz);
  }
}

void writeToGyro(int DEVICE, byte address, byte val) {
  Wire.beginTransmission(DEVICE); //start transmission to ACC 
  Wire.write(address);        // send register address
  Wire.write(val);        // send value to write
  Wire.endTransmission(); //end transmission
}
//reads num bytes starting from address register on ACC in to buff array
 void readFromGyro(int DEVICE, byte address, int num, byte buff[]) {
 Wire.beginTransmission(DEVICE); //start transmission to ACC 
 Wire.write(address);        //sends address to read from
 Wire.endTransmission(); //end transmission
 
 Wire.beginTransmission(DEVICE); //start transmission to ACC
 Wire.requestFrom(DEVICE, num);    // request 6 bytes from ACC
 
 int i = 0;
 while(Wire.available())    //ACC may send less than requested (abnormal)
 { 
   buff[i] = Wire.read(); // receive a byte
   i++;
 }
 Wire.endTransmission(); //end transmission
}

/****** DATA COLLECTION ******/
void dataCollection(){
  //Goes through the list of characters
  for(int thisChar = 0; thisChar < CHARCOUNT; thisChar++){ 
    //Message for the user and 3 seconds delay before character reading
    Serial.print(CHARACTERS[thisChar]);
    Serial.println(" in 5s");
    delay(5000);
    for(int n = 0; n < SAMPLE_SIZE; n++){
      //Prints current character
      displayValues();
      Serial.print(",");
      Serial.println(CHARACTERS[thisChar]);
      delay (10);
    }    
  }  
}
