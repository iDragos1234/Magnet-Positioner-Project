#include <EEPROM.h>
#include <AccelStepper.h>

// Define motor driver type (1 = Driver, uses STEP and DIR)
#define DRIVER 1

// Stepper motor definitions (STEP, DIR)
AccelStepper stepperX(DRIVER, 2, 5);  // X-axis
AccelStepper stepperY(DRIVER, 3, 6);  // Y-axis
AccelStepper stepperZ(DRIVER, 4, 7);  // Z-axis


const byte limitPin = A2;   // input pin for limit switch, change to your needs
                            // Switch must connect to GND if stepper reaches the switch.
                            
// CNC Shield Enable Pin (shared for all motors)
const int enPin = 8; // ENABLE pin for all motors

// EEPROM Addresses
constexpr int EEPROM_ADDR[] = {0, 4, 8}; // x, y, z

// Stepper motor settings (individual for each axis)
// constexpr int maxSpeedX = 100;   // X max speed (steps per second)
constexpr int maxSpeedX = 1000;   // X max speed (steps per second)
// constexpr int accelerationX = 100; // X acceleration (steps per second²)
constexpr int accelerationX = 2*maxSpeedX; // X acceleration (steps per second²)

constexpr int maxSpeedY = 1000;   // Y max speed (steps per second)
constexpr int accelerationY = 2 * maxSpeedY; // Y acceleration (steps per second²)

constexpr int maxSpeedZ = 500;   // Z max speed (steps per second)
constexpr int accelerationZ = 500; // Z acceleration (steps per second²)

// Array of stepper motor pointers for easier handling
AccelStepper* steppers[] = {&stepperX, &stepperY, &stepperZ};

// Motor axis labels
constexpr char AXIS_LABELS[] = {'x', 'y', 'z'};

void setup() {
    Serial.begin(9600);

    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(enPin, OUTPUT);

    // Disable motors at startup
    // Configure all steppers
    configureStepper(stepperX, maxSpeedX, accelerationX);
    configureStepper(stepperY, maxSpeedY, accelerationY);
    configureStepper(stepperZ, maxSpeedZ, accelerationZ);

    // // Uncomment below if there is a limit switch
    // stepperX.moveTo(-250);                // should be max possible movement towards the limit switch
    // while( digitalRead( limitPin ) == HIGH ) stepper.run(); // move until limit switch is reached
    // stepperX.setCurrentPosition( -256 );    // set current position as negative limit
    disableMotors();
}

// Configure stepper motor parameters
void configureStepper(AccelStepper &stepper, int maxSpeed, int acceleration) {
    stepper.setMaxSpeed(maxSpeed);
    stepper.setAcceleration(acceleration);
}

// Disable all motors (turns off holding torque)
void disableMotors() {
    digitalWrite(enPin, HIGH); // Disable all motors
}

// Enable motors before movement
void enableMotors() {
    digitalWrite(enPin, LOW); // Enable all motors
}

// Handle LED control commands
void handleLEDCommand(String command) {
    if (command == "L0") {
        digitalWrite(LED_BUILTIN, LOW);
        Serial.println("0");
    } else if (command == "L1") {
        digitalWrite(LED_BUILTIN, HIGH);
        Serial.println("1");
    } else if (command == "L?") {
        Serial.println(digitalRead(LED_BUILTIN) ? "1" : "0");
    } else {
        Serial.println("Invalid L command. Use L0, L1, or L?");
    }
}

  

// Handle movement and position queries for an axis
void handleAxisCommand(String command, int axisIndex) {
    if (command.endsWith("?")) {
        long stored_value;
        EEPROM.get(EEPROM_ADDR[axisIndex], stored_value);
        Serial.println(stored_value);
    } else {
        long value = command.substring(1).toInt();
        updatePosition(AXIS_LABELS[axisIndex], value);
    }
}

// Handle tare commands
void handleTareCommand(String command) {
    for (int i = 0; i < 3; i++) {
        if (command == "t" + String(AXIS_LABELS[i])) {
            EEPROM.put(EEPROM_ADDR[i], 0L);
            Serial.println(command);
            return;
        }
    }
    Serial.println("Invalid tare command: " + command);
}

// Move motor and update EEPROM
void updatePosition(char axis, long new_position) {
    int axisIndex = getAxisIndex(axis);
    if (axisIndex == -1) {
        Serial.println("Invalid axis");
        return;
    }

    long current_position;
    EEPROM.get(EEPROM_ADDR[axisIndex], current_position);

    if (current_position != new_position) { // Only move if position changes
        stepMotor(*steppers[axisIndex], new_position - current_position);
        EEPROM.put(EEPROM_ADDR[axisIndex], new_position);
    }
    Serial.println(axis);
}

// Step motor with acceleration
void stepMotor(AccelStepper &stepper, long steps) {
   // Enable motors before movement
    enableMotors();

    long targetPosition = stepper.currentPosition() + steps;
    stepper.moveTo(targetPosition);

    while (stepper.distanceToGo() != 0) {
        stepper.run();
    }
    disableMotors();
}

// Get the index of the axis ('x', 'y', 'z') for use in arrays
int getAxisIndex(char axis) {
    for (int i = 0; i < 3; i++) {
        if (AXIS_LABELS[i] == axis) return i;
    }
    return -1; // Invalid axis
}

void loop() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();

        char cmdType = command.charAt(0);

        // LED Commands
        if (cmdType == 'L') {
            handleLEDCommand(command);
            return;
        }

        // Axis Movement Commands
        int axisIndex = getAxisIndex(cmdType);
        if (axisIndex != -1) {
            handleAxisCommand(command, axisIndex);
            return;
        }

        // Tare Commands
        if (cmdType == 't') {
            handleTareCommand(command);
            return;
        }


        Serial.println("Invalid command " + command);
    }
}
