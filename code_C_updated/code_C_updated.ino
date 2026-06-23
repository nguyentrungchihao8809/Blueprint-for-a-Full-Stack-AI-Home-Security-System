#include <LiquidCrystal.h>
#include <DHT.h>

const uint8_t LCD_RS = 12;
const uint8_t LCD_EN = 11;
const uint8_t LCD_D4 = 7;
const uint8_t LCD_D5 = 6;
const uint8_t LCD_D6 = 5;
const uint8_t LCD_D7 = 4;
LiquidCrystal lcd(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7);

#define DHT_PIN 2
#define DHT_TYPE DHT11
DHT dht(DHT_PIN, DHT_TYPE);

#define GAS_PIN A0
#define PIR_PIN 3        
#define DOOR_PIN 8      
#define LED_PIN 9
#define BUZZER_PIN 10

const float CRITICAL_TEMP = 75.0;
const int CRITICAL_GAS = 300;

bool manualLED = false;
bool manualBuzzer = false;

int acTemp = 0;
int personCount = 0;

unsigned long previousMillis = 0;   
const long INTERVAL = 2500;  

int lastPirState = LOW;
int lastDoorState = HIGH;

float currentTemp = 0.0;
float currentHumid = 0.0;

// Ham in du lieu ngay lap tuc
void printData(int pirState, int doorState, int gasPPM) {
  Serial.print("TEMP:");   Serial.print(currentTemp);
  Serial.print("|HUMID:"); Serial.print(currentHumid);
  Serial.print("|GAS:");   Serial.print(gasPPM);
  Serial.print("|PIR:");   Serial.print(pirState);
  Serial.print("|DOOR:");  Serial.print(doorState);
  Serial.print("|AC:");    Serial.print(acTemp);
  Serial.print("|PERSON:"); Serial.println(personCount);
}

void setup() {
  Serial.begin(9600);
  delay(500);
  
  lcd.begin(16, 2);
  lcd.print("Smart Home AI");
  lcd.setCursor(0, 1);
  lcd.print("System Ready...");
  
  pinMode(PIR_PIN, INPUT);
  pinMode(DOOR_PIN, INPUT_PULLUP); 
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  
  dht.begin();
  delay(2000); 
  lcd.clear();
}

void loop() {
  int pirState = digitalRead(PIR_PIN);
  int doorState = digitalRead(DOOR_PIN);
  int gasAnalog = analogRead(GAS_PIN);
  int gasPPM = map(gasAnalog, 0, 1023, 0, 1000);

  if (Serial.available() > 0) {
    while (Serial.available() > 0) {
      char receivedChar = Serial.read();
      Serial.print("RX:");
      Serial.println(receivedChar);

      if (receivedChar == '\n' || receivedChar == '\r') {
        continue;
      }

      switch (receivedChar) {
        case '1':
          manualLED = true;
          Serial.println("EVENT:LED_ON");
          printData(pirState, doorState, gasPPM);
          Serial.flush();
          break;
        case '2':
          manualLED = false;
          Serial.println("EVENT:LED_OFF");
          printData(pirState, doorState, gasPPM);
          Serial.flush();
          break;
        case '3':
          manualBuzzer = true;
          Serial.println("EVENT:BUZZER_ON");
          printData(pirState, doorState, gasPPM);
          Serial.flush();
          break;
        case '4':
          manualBuzzer = false;
          Serial.println("EVENT:BUZZER_OFF");
          printData(pirState, doorState, gasPPM);
          Serial.flush();
          break;
        case '5':
          acTemp = 26;
          personCount = 1;
          Serial.println("EVENT:AC_26C");
          printData(pirState, doorState, gasPPM);
          Serial.flush();
          break;
        case '6':
          acTemp = 24;
          personCount = 3;
          Serial.println("EVENT:AC_24C");
          printData(pirState, doorState, gasPPM);
          Serial.flush();
          break;
        case '7':
          acTemp = 0;
          personCount = 0;
          Serial.println("EVENT:AC_OFF");
          printData(pirState, doorState, gasPPM);
          Serial.flush();
          break;
        default:
          break;
      }
    }
  }

  bool isFireDanger = (currentTemp > CRITICAL_TEMP || gasPPM > CRITICAL_GAS);
  digitalWrite(LED_PIN, (isFireDanger || manualLED) ? HIGH : LOW);
  digitalWrite(BUZZER_PIN, (isFireDanger || manualBuzzer) ? HIGH : LOW);

  if (pirState == HIGH && lastPirState == LOW) {
    Serial.println("EVENT:MOTION_DETECTED");
  }
  lastPirState = pirState;

  if (doorState == HIGH && lastDoorState == LOW) {
    Serial.println("EVENT:DOOR_OPENED");
  }
  lastDoorState = doorState;

  unsigned long currentMillis = millis(); 
  if (currentMillis - previousMillis >= INTERVAL) {
    previousMillis = currentMillis; 

    float rawHumid = dht.readHumidity();
    float rawTemp = dht.readTemperature();
    
    if (!isnan(rawTemp) && rawTemp > -40.0 && rawTemp < 125.0) {
      currentTemp = rawTemp;
    }
    if (!isnan(rawHumid)) {
      currentHumid = rawHumid;
    }

    lcd.setCursor(0, 0);
    lcd.print("T:"); lcd.print((int)currentTemp); lcd.print("C ");
    lcd.print("H:"); lcd.print((int)currentHumid); lcd.print("%  ");
    
    lcd.setCursor(0, 1);
    if (acTemp == 0) {
      lcd.print("AC:OFF P:");
      lcd.print(personCount);
      lcd.print("      ");
    } else {
      lcd.print("AC:");
      lcd.print(acTemp);
      lcd.print("C P:");
      lcd.print(personCount);
      lcd.print("     ");
    }

    printData(pirState, doorState, gasPPM);
  }
}
