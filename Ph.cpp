#include <ESP8266WiFi.h>
#include <EEPROM.h>

// --- WiFi Configuration ---
const char* ssid = "YOUR_WIFI_SSID";         // Replace with your WiFi network SSID
const char* password = "YOUR_WIFI_PASSWORD"; // Replace with your WiFi password

// --- pH Sensor Configuration ---
const int pH_sensor_pin = A0;       // Analog pin for pH sensor
const float calibration_voltage_7 = 2.05; // Voltage at pH 7.0 
const float calibration_voltage_4 = 1.65; // Voltage at pH 4.0 

// --- Solenoid Valve Configuration ---
const int base_valve_pin = D2;     // Digital pin for base solenoid valve
const int acid_valve_pin = D3;     // Digital pin for acid solenoid valve
const unsigned long valve_activation_time = 2000; // Milliseconds to activate valve

// --- pH Target Range Configuration ---
float target_pH_low;
float target_pH_high;

// --- EEPROM Configuration ---
const int EEPROM_SIZE = 128;
const int PH_LOW_ADDR = 0;
const int PH_HIGH_ADDR = 4;

// --- Global Variables ---
unsigned long last_pH_read_time = 0;
const unsigned long pH_read_interval = 5000; // Read pH every 5 seconds

unsigned long last_valve_activation_time = 0;
bool base_valve_active = false;
bool acid_valve_active = false;

// --- Function Declarations ---
float read_pH();
void control_pH(float current_pH);
void save_pH_range();
void load_pH_range();
void handle_serial_input();
void connect_wifi();
void print_pH_range();

void setup() {
  Serial.begin(115200);
  delay(10);

  pinMode(base_valve_pin, OUTPUT);
  pinMode(acid_valve_pin, OUTPUT);
  digitalWrite(base_valve_pin, LOW);  // Normally closed
  digitalWrite(acid_valve_pin, LOW);  // Normally closed

  EEPROM.begin(EEPROM_SIZE);
  load_pH_range();
  print_pH_range();

  connect_wifi();
}

void loop() {
  handle_serial_input();

  unsigned long current_time = millis();
  if (current_time - last_pH_read_time >= pH_read_interval) {
    last_pH_read_time = current_time;
    float current_pH = read_pH();
    Serial.print("Current pH: ");
    Serial.println(current_pH);
    control_pH(current_pH);
  }

  // Non-blocking valve deactivation
  if (base_valve_active && (current_time - last_valve_activation_time >= valve_activation_time)) {
    digitalWrite(base_valve_pin, LOW);
    base_valve_active = false;
    Serial.println("Base valve deactivated.");
  }

  if (acid_valve_active && (current_time - last_valve_activation_time >= valve_activation_time)) {
    digitalWrite(acid_valve_pin, LOW);
    acid_valve_active = false;
    Serial.println("Acid valve deactivated.");
  }

  delay(10); // Small delay to prevent busy-waiting
}

void connect_wifi() {
  Serial.println("\nConnecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

float read_pH() {
  int analog_value = analogRead(pH_sensor_pin);
  float voltage = analog_value / 1023.0 * 3.3; // Assuming ESP8266 ADC range is 0-3.3V

  // Linear interpolation for pH calculation
  float pH = 7.0 - (voltage - calibration_voltage_7) * (7.0 - 4.0) / (calibration_voltage_7 - calibration_voltage_4);
  return pH;
}

void control_pH(float current_pH) {
  unsigned long current_time = millis();

  if (!base_valve_active && !acid_valve_active) {
    if (current_pH < target_pH_low) {
      Serial.println("pH too low, activating base valve.");
      digitalWrite(base_valve_pin, HIGH);
      base_valve_active = true;
      last_valve_activation_time = current_time;
    } else if (current_pH > target_pH_high) {
      Serial.println("pH too high, activating acid valve.");
      digitalWrite(acid_valve_pin, HIGH);
      acid_valve_active = true;
      last_valve_activation_time = current_time;
    }
  }
}

void save_pH_range() {
  EEPROM.put(PH_LOW_ADDR, target_pH_low);
  EEPROM.put(PH_HIGH_ADDR, target_pH_high);
  EEPROM.commit();
  Serial.println("pH range saved to EEPROM.");
  print_pH_range();
}

void load_pH_range() {
  EEPROM.get(PH_LOW_ADDR, target_pH_low);
  EEPROM.get(PH_HIGH_ADDR, target_pH_high);
  Serial.println("pH range loaded from EEPROM.");
}

void handle_serial_input() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toLowerCase();

    if (command.startsWith("setph")) {
      int comma_index = command.indexOf(',');
      if (comma_index > 5) {
        String low_str = command.substring(5, comma_index);
        String high_str = command.substring(comma_index + 1);
        target_pH_low = low_str.toFloat();
        target_pH_high = high_str.toFloat();
        save_pH_range();
      } else {
        Serial.println("Invalid setph command. Use 'setph low,high' (e.g., 'setph 6.5,7.5').");
      }
    } else if (command.equals("getph")) {
      print_pH_range();
    } else if (command.equals("save")) {
      save_pH_range();
    } else if (command.equals("load")) {
      load_pH_range();
      print_pH_range();
    } else {
      Serial.println("Available commands: setph low,high, getph, save, load");
    }
  }
}

void print_pH_range() {
  Serial.print("Target pH Range: ");
  Serial.print(target_pH_low);
  Serial.print(" to ");
  Serial.println(target_pH_high);
}
