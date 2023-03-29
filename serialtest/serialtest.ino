void setup() {
  Serial.begin(9600);
}

void loop() {
  while(Serial.available()) {
    String line = Serial.readString();
    Serial.print(line);
    // Motor Control
  }
}
