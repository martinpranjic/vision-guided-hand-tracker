#include <Servo.h>

Servo panServo;
Servo tiltServo;

const int PAN_SERVO_PIN = 9;
const int TILT_SERVO_PIN = 10;

void setup() {
    Serial.begin(115200);
    
    panServo.attach(PAN_SERVO_PIN);
    tiltServo.attach(TILT_SERVO_PIN);

    panServo.write(90);
    tiltServo.write(90);
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');

        int commaPosition = command.indexOf(',');

        if (commaPosition != -1) {
            int panAngle = command.substring(0, commaPosition).toInt();
            int tiltAngle = command.substring(commaPosition + 1).toInt();

            panAngle = constrain(panAngle, 0, 180);
            tiltAngle = constrain(tiltAngle, 0, 180);

            panServo.write(panAngle);
            tiltServo.write(tiltAngle);

            Serial.print(panAngle);
            Serial.print(",");
            Serial.println(tiltAngle);
        }
    }
}