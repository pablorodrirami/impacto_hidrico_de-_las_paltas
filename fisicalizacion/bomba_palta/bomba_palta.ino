// Vertido por palta: cada palta NUEVA frente a la cámara suma 15 segundos de chorro continuo.
// El agua ya "gastada" no se devuelve: si sacas la palta, el vertido sigue hasta completar su tiempo.
//
// Recibe por USB (la página lo manda cada 200 ms):
//   '0' … '9'  cantidad de paltas que ve la cámara
//   'x'        la cámara no está entregando imagen → pausa (no cuenta como sacar las paltas)
//
// Seguridad: si pasa 1 segundo sin recibir nada (se cerró la página, se cayó el USB), la bomba
// se PAUSA y el tiempo que faltaba se guarda; cuando vuelve la conexión sigue sola.

const int RELE = 7;                            // HIGH = relé apagado (el módulo se activa con LOW)
const unsigned long MS_POR_PALTA = 15000;      // 15 s de chorro por cada palta nueva
const unsigned long ESPERA_QUITAR_MS = 2000;   // una palta debe faltar 2 s para darla por sacada
                                               // (evita cobrar dos veces si la cámara parpadea)
const unsigned long MAX_PENDIENTE_MS = 180000; // tope de seguridad: 3 min de vertido acumulado
const unsigned long SIN_DATOS_MS = 1000;       // watchdog

int paltasRecibidas = 0;        // lo último que mandó la página
int paltasContadas = 0;         // paltas que ya sumaron su tiempo
bool camaraOk = false;
unsigned long ultimoDato = 0;
bool bajando = false;           // hay menos paltas que las contadas…
unsigned long desdeBajando = 0; // …desde este momento
unsigned long pendienteMs = 0;  // tiempo de chorro que falta
unsigned long ultimoLoop = 0;
bool encendida = false;

void setup() {
  pinMode(RELE, OUTPUT);
  digitalWrite(RELE, HIGH);
  Serial.begin(9600);
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c >= '0' && c <= '9') { paltasRecibidas = c - '0'; camaraOk = true;  ultimoDato = millis(); }
    else if (c == 'x')        {                            camaraOk = false; ultimoDato = millis(); }
  }

  unsigned long ahora = millis();
  unsigned long dt = ahora - ultimoLoop;
  ultimoLoop = ahora;

  // descontar el tiempo que estuvo encendida desde la vuelta anterior
  if (encendida) pendienteMs = (dt >= pendienteMs) ? 0 : pendienteMs - dt;

  bool activo = (ahora - ultimoDato <= SIN_DATOS_MS) && camaraOk;

  if (activo) {
    if (paltasRecibidas > paltasContadas) {                 // palta(s) nueva(s): sumar su agua
      pendienteMs += (unsigned long)(paltasRecibidas - paltasContadas) * MS_POR_PALTA;
      if (pendienteMs > MAX_PENDIENTE_MS) pendienteMs = MAX_PENDIENTE_MS;
      paltasContadas = paltasRecibidas;
      bajando = false;
    } else if (paltasRecibidas < paltasContadas) {          // ¿sacaron paltas? esperar a confirmarlo
      if (!bajando) { bajando = true; desdeBajando = ahora; }
      else if (ahora - desdeBajando >= ESPERA_QUITAR_MS) { paltasContadas = paltasRecibidas; bajando = false; }
    } else {
      bajando = false;
    }
  }

  encendida = activo && pendienteMs > 0;
  digitalWrite(RELE, encendida ? LOW : HIGH);
}
