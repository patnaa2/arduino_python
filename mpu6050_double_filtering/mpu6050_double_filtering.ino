// I2C device class (I2Cdev) demonstration Arduino sketch for MPU6050 class
// 10/7/2011 by Jeff Rowberg <jeff@rowberg.net>
// Updates should (hopefully) always be available at https://github.com/jrowberg/i2cdevlib
//
// Changelog:
//      2013-05-08 - added multiple output formats
//                 - added seamless Fastwire support
//      2011-10-07 - initial release

/* ============================================
I2Cdev device library code is placed under the MIT license
Copyright (c) 2011 Jeff Rowberg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
===============================================
*/

// I2Cdev and MPU6050 must be installed as libraries, or else the .cpp/.h files
// for both classes must be in the include path of your project
#include "I2Cdev.h"
#include "MPU6050.h"

// Arduino Wire library is required if I2Cdev I2CDEV_ARDUINO_WIRE implementation
// is used in I2Cdev.h
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

// class default I2C address is 0x68
// specific I2C addresses may be passed as a parameter here
// AD0 low = 0x68 (default for InvenSense evaluation board)
// AD0 high = 0x69
MPU6050 accelgyro1(0x68);
MPU6050 accelgyro2(0x69);

const float WEIGHT = 0.8;

int16_t ax1, ay1, az1;
int16_t gx1, gy1, gz1;

int16_t ax2, ay2, az2;
int16_t gx2, gy2, gz2;            

int16_t old_ax1, old_ay1, old_az1;
int16_t old_gx1, old_gy1, old_gz1;

int16_t old_ax2, old_ay2, old_az2;
int16_t old_gx2, old_gy2, old_gz2;


// uncommMent for accelero values
//#define OUTPUT_READABLE_ACCEL

// uncomment for gyro values
#define OUTPUT_READABLE_GYRO

#define LED_PIN 13
bool blinkState = false;

void setup() {
    // join I2C bus (I2Cdev library doesn't do this automatically)
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
    #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
    #endif

    // initialize serial communication
    // (38400 chosen because it works as well at 8MHz as it does at 16MHz, but
    // it's really up to you depending on your project)
    Serial.begin(112500);

    // initialize device
    //Serial.println("Initializing I2C devices...");
    accelgyro1.initialize();
    accelgyro2.initialize();
  
    // verify connection
    //Serial.println("Testing device connections...");
    //Serial.println(accelgyro1.testConnection() ? "MPU6050 1 connection successful" : "MPU6050 1 connection failed");
    //Serial.println(accelgyro2.testConnection() ? "MPU6050 2 High connection successful" : "MPU6050 2 High connection failed");

    // use the code below to change accel/gyro offset values
    /*
    Serial.println("Updating internal sensor offsets...");
    // -76	-2359	1688	0	0	0
    Serial.print(accelgyro1.getXAccelOffset()); Serial.print("\t"); // -76
    Serial.print(accelgyro1.getYAccelOffset()); Serial.print("\t"); // -2359
    Serial.print(accelgyro1.getZAccelOffset()); Serial.print("\t"); // 1688
    Serial.print(accelgyro1.getXGyroOffset()); Serial.print("\t"); // 0
    Serial.print(accelgyro1.getYGyroOffset()); Serial.print("\t"); // 0
    Serial.print(accelgyro1.getZGyroOffset()); Serial.print("\t"); // 0 
    Serial.print("\n");
    Serial.print(accelgyro2.getXAccelOffset()); Serial.print("\t"); // -76
    Serial.print(accelgyro2.getYAccelOffset()); Serial.print("\t"); // -2359
    Serial.print(accelgyro2.getZAccelOffset()); Serial.print("\t"); // 2688
    Serial.print(accelgyro2.getXGyroOffset()); Serial.print("\t"); // 0
    Serial.print(accelgyro2.getYGyroOffset()); Serial.print("\t"); // 0
    Serial.print(accelgyro2.getZGyroOffset()); Serial.print("\t"); // 0
    Serial.print("\n");
    accelgyro1.setXAccelOffset(3340);
    accelgyro1.setYAccelOffset(785);
    accelgyro1.setZAccelOffset(-2056);
    accelgyro2.setXAccelOffset(1940);
    accelgyro2.setYAccelOffset(3081);
    accelgyro2.setZAccelOffset(-1024);
    //accelgyro.setXGyroOffset(220);
    //accelgyro.setYGyroOffset(76);
    //accelgyro.setZGyroOffset(-85);
    
    
    Serial.print("\n");
    */

    // configure Arduino LED for
    pinMode(LED_PIN, OUTPUT);
}

void loop() {
    // read raw accel/gyro measurements from device
    accelgyro1.getMotion6(&ax1, &ay1, &az1, &gx1, &gy1, &gz1);
    accelgyro2.getMotion6(&ax2, &ay2, &az2, &gx2, &gy2, &gz2);

    // these methods (and a few others) are also available
    //accelgyro.getAcceleration(&ax, &ay, &az);
    //accelgyro.getRotation(&gx, &gy, &gz);

    #ifdef OUTPUT_READABLE_ACCEL
        ax1 = (1 - WEIGHT) * old_ax1 + (WEIGHT * ax1);
        ax2 = (1 - WEIGHT) * old_ax2 + (WEIGHT * ax2);
        ay1 = (1 - WEIGHT) * old_ay1 + (WEIGHT * ay1);
        ay2 = (1 - WEIGHT) * old_ay2 + (WEIGHT * ay2);
        az1 = (1 - WEIGHT) * old_az1 + (WEIGHT * az1);
        az2 = (1 - WEIGHT) * old_az2 + (WEIGHT * az2);
        
        Serial.print(ax1); Serial.print(" ");
        Serial.print(ay1); Serial.print(" ");
        Serial.print(az1); Serial.print(" ");
        Serial.print("|");
        Serial.print(ax2); Serial.print(" ");  
        Serial.print(ay2); Serial.print(" ");
        Serial.println(az2);
        
        old_ax1 = ax1;
        old_ax2 = ax2;
        old_ay1 = ay1;
        old_ay2 = ay2;
        old_az1 = az1;
        old_ax2 = az2;
    #endif
    
    #ifdef OUTPUT_READABLE_GYRO
        gx1 = (1 - WEIGHT) * old_gx1 + (WEIGHT * gx1);
        gx2 = (1 - WEIGHT) * old_gx2 + (WEIGHT * gx2);
        gy1 = (1 - WEIGHT) * old_gy1 + (WEIGHT * gy1);
        gy2 = (1 - WEIGHT) * old_gy2 + (WEIGHT * gy2);
        gz1 = (1 - WEIGHT) * old_gz1 + (WEIGHT * gz1);
        gz2 = (1 - WEIGHT) * old_gz2 + (WEIGHT * gz2);  
        
            
        Serial.print(gx1); Serial.print(" ");
        Serial.print(gy1); Serial.print(" ");
        Serial.print(gz1); Serial.print(" ");
        Serial.print("|");
        Serial.print(gx2); Serial.print(" ");
        Serial.print(gy2); Serial.print(" ");
        Serial.println(gz2);
    
        old_gx1 = gx1;
        old_gx2 = gx2;
        old_gy1 = gy1;
        old_gy2 = gy2;
        old_gz1 = gz1;
        old_gx2 = gz2;  
    #endif

    // blink LED to indicate activity
    blinkState = !blinkState;
    digitalWrite(LED_PIN, blinkState);
}
