// Recibe por USB: '1' = bomba ON, '0' = bomba OFF.
// Si pasa 1 segundo sin recibir nada (por ejemplo, se cerró el programa), apaga la bomba sola.
const int RELE = 7;
unsigned long ultimo = 0;

void setup() {
  pinMode(RELE, OUTPUT);
  digitalWrite(RELE, HIGH);   // HIGH = relé apagado (tu módulo activa con LOW)
  Serial.begin(9600);
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '1') { digitalWrite(RELE, LOW);  ultimo = millis(); }
    if (c == '0') { digitalWrite(RELE, HIGH); ultimo = millis(); }
  }
  if (millis() - ultimo > 1000) digitalWrite(RELE, HIGH);
}
