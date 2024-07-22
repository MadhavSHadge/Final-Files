#include <Arduino.h>

const int enablePin = 9;    // PWM pin for motor speed control
const int int1Pin = 8;      // Motor driver input 1
const int int2Pin = 7;      // Motor driver input 2

int speed = 0;              // Global variable to hold speed

int encoderPin1 = 2;
int encoderPin2 = 3;

volatile long encoderValue = 0;

long maximumEncoderValue = 0;
int gearRatio = 0;

void setup() {
  Serial.begin(9600);
  pinMode(enablePin, OUTPUT);
  pinMode(int1Pin, OUTPUT);
  pinMode(int2Pin, OUTPUT);

  pinMode(encoderPin1, INPUT_PULLUP);
  pinMode(encoderPin2, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(encoderPin1), updateEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(encoderPin2), updateEncoder, CHANGE);
}

void loop() {
  if (Serial.available() > 0) {
    int antennaAngle = Serial.parseInt();
    Serial.print("Received Antenna Angle: ");
    Serial.println(antennaAngle);

    while (Serial.available() == 0) {}
    int newPulses = Serial.parseInt();
    Serial.print("Pulse count per revolution: ");
    Serial.println(newPulses);

    while (Serial.available() == 0) {}
    gearRatio = Serial.parseInt();
    Serial.print("Gear Ratio: ");
    Serial.println(gearRatio);

    // Convert antenna angle to pulses
    long pulsesPerRevolution = newPulses * 4;
    maximumEncoderValue = pulsesPerRevolution * gearRatio/360;

    // Motor control based on user input
    char command = Serial.read();
    switch (command) {
      case 'F':  // Forward
        forward(speed);
        Serial.println("Forward direction");
        break;
      case 'B':  // Backward
        backward(speed);
        Serial.println("Backward direction");
        break;
      case 'S':  // Stop
        stopMotor();
        Serial.println("Stop motor");
        break;
      case 'D':  // Direction check
        directionCheck(encoderValue);
        break;
      case 'P':
        // Code to set pulses per revolution
        break;
      case 'G':
        // Code to set gear ratio
        break;
      case 'A':
        // Code to set antenna angle
        break;
      case 'D':
        // Code for direction count
        break;
      case 'R':
        // Code to reset parameters
        break;
      default:
        // Handle unknown command
        break;
    }
  }
}

void updateEncoder() {
  static int lastEncoded = 0;
  int MSB = digitalRead(encoderPin1);
  int LSB = digitalRead(encoderPin2);
  int encoded = (MSB << 1) | LSB;
  int sum = (lastEncoded << 2) | encoded;

  if (sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011)
    encoderValue++;
  if (sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000)
    encoderValue--;

  lastEncoded = encoded;
}

void forward(int speed) {
  long targetEncoderValue = encoderValue + maximumEncoderValue;
  while (encoderValue <= targetEncoderValue) {
    analogWrite(enablePin, speed);
    digitalWrite(int1Pin, HIGH);
    digitalWrite(int2Pin, LOW);
  }
  stopMotor();
}

void backward(int speed) {
  long targetEncoderValue = encoderValue - maximumEncoderValue;
  while (encoderValue >= targetEncoderValue) {
    analogWrite(enablePin, speed);
    digitalWrite(int1Pin, LOW);
    digitalWrite(int2Pin, HIGH);
  }
  stopMotor();
}

void stopMotor() {
  digitalWrite(int1Pin, LOW);
  digitalWrite(int2Pin, LOW);
}

void directionCheck(long currentEncoderValue) {
  static long previousEncoderValue = 0;

  if (currentEncoderValue > previousEncoderValue) {
    Serial.println("Clockwise Direction");
  } else if (currentEncoderValue < previousEncoderValue) {
    Serial.println("Anti-Clockwise Direction");
  } else {
    Serial.println("No Change in Direction");
  }
  previousEncoderValue = currentEncoderValue;
}
