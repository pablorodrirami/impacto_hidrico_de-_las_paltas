import cv2
import numpy as np
import time
import json
import os
import threading
from collections import deque
from http.server import BaseHTTPRequestHandler, HTTPServer
import serial   # pip install pyserial

# ===================== CONFIGURACIÓN =====================
URL = "http://220.171.77.181:8080/video"   # IP Webcam
PUERTO = "COM10"        # puerto del Arduino (el que ves en Arduino IDE). None = correr sin Arduino
MARGEN = 30
ML_POR_PALTA = 110     # 1 palta = 110 mL de agua (representa 110 L reales)
L_REALES_POR_PALTA = 110
CAUDAL_ML_S = 25       # IMPORTANTE: caudal REAL de tu bomba en mL/s (ajústalo, ver instrucciones)
CAPACIDAD = 1000       # mL que caben en el tupper (el nivel máximo)
ESCALA = 0.35
# =========================================================
 
# ---------- Arduino (hilo propio: mantiene la conexión viva todo el tiempo) ----------
# El bucle de la cámara solo dice qué quiere (deseo_bomba). Este hilo, independiente de la
# cámara, le manda ese estado al Arduino cada 200 ms y, si la conexión se cae, CIERRA el
# puerto y lo vuelve a abrir solo, sin congelar la cámara ni la página.
from serial.tools import list_ports

ENVIO_S = 0.2            # cada cuánto se le habla al Arduino (su watchdog corta a 1 s)
ORDEN_VIGENTE_S = 1.0    # si la cámara no actualiza en este tiempo, la bomba se apaga por seguridad

deseo_bomba = False      # lo que quiere el bucle de la cámara
ultima_orden = 0.0       # cuándo lo actualizó por última vez
arduino_ok = False       # True si la última escritura funcionó
detener = threading.Event()

def buscar_puerto():
    """Usa PUERTO; si no aparece (Windows a veces cambia el COM al reconectar el USB), busca un Arduino."""
    puertos = list(list_ports.comports())
    if any(p.device == PUERTO for p in puertos):
        return PUERTO
    for p in puertos:
        texto = (str(p.description) + " " + str(p.manufacturer)).lower()
        if p.vid in (0x2341, 0x2A03, 0x1A86, 0x0403) or any(s in texto for s in ("arduino", "ch340", "usb-serial", "usb serial")):
            return p.device
    return None

def hilo_arduino():
    global arduino_ok
    conexion = None
    ultimo_aviso = None

    def avisar(msg):               # imprime solo cuando el mensaje cambia (no llena la consola)
        nonlocal ultimo_aviso
        if msg != ultimo_aviso:
            print(msg)
            ultimo_aviso = msg

    def cerrar():
        nonlocal conexion
        try:
            conexion.close()       # CLAVE: liberar el COM, si no Windows no deja reabrirlo
        except Exception:
            pass
        conexion = None

    while not detener.is_set():
        if conexion is None:
            arduino_ok = False
            puerto = buscar_puerto()
            if puerto is None:
                avisar("Arduino no encontrado (¿USB desconectado?). Reintentando…")
                detener.wait(1)
                continue
            try:
                conexion = serial.Serial(puerto, 9600, timeout=0, write_timeout=0.5)
                detener.wait(2)    # el Arduino se reinicia al abrir el puerto
                conexion.reset_input_buffer()
                avisar("Arduino conectado en " + puerto)
            except Exception as e:
                if conexion is not None:
                    cerrar()
                avisar("No se pudo abrir " + puerto + " -> " + str(e) +
                       "  (¿Monitor Serie del IDE abierto?) Reintentando…")
                detener.wait(1)
                continue

        encender = deseo_bomba and (time.time() - ultima_orden < ORDEN_VIGENTE_S)
        try:
            conexion.write(b"1" if encender else b"0")
            arduino_ok = True
        except Exception as e:
            avisar("Se cayó la conexión con el Arduino -> " + str(e) + "  Reconectando…")
            cerrar()
            arduino_ok = False
            detener.wait(0.5)
            continue
        detener.wait(ENVIO_S)

    # Al salir: apagar la bomba y soltar el puerto
    if conexion is not None:
        try:
            conexion.write(b"0")
            conexion.flush()
        except Exception:
            pass
        cerrar()
    arduino_ok = False

hilo_serial = None
if PUERTO:
    hilo_serial = threading.Thread(target=hilo_arduino, daemon=True)
    hilo_serial.start()

# ---------- Servidor web (sirve index.html y el estado) ----------
estado = {"paltas": 0, "nivel": 0, "capacidad": CAPACIDAD, "bomba": False,
          "arduino": False if PUERTO else None, "camara": False,
          "litros_reales": 0, "ml_por_palta": ML_POR_PALTA, "l_por_palta": L_REALES_POR_PALTA}
carpeta = os.path.dirname(os.path.abspath(__file__))
 
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/estado"):
            datos = json.dumps(estado).encode()
            tipo = "application/json"
        else:
            with open(os.path.join(carpeta, "index.html"), "rb") as f:
                datos = f.read()
            tipo = "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(datos)
    def log_message(self, *args):
        pass   # no llenar la consola de mensajes
 
servidor = HTTPServer(("0.0.0.0", 8000), Handler)
threading.Thread(target=servidor.serve_forever, daemon=True).start()
print("Página lista en http://localhost:8000")
 
# ---------- Cámara ----------
def abrir_camara():
    """Insiste hasta abrir la cámara (no cierra el programa si el celular tarda o se cae el Wi-Fi)."""
    while True:
        c = cv2.VideoCapture(URL)
        if c.isOpened():
            print("Cámara conectada")
            return c
        c.release()
        print("No se pudo abrir la cámara. Revisa la IP y que IP Webcam esté iniciado. Reintentando…")
        time.sleep(3)

cap = abrir_camara()
 
kernel = np.ones((7, 7), np.uint8)
def nada(x):
    pass
 
cv2.namedWindow("Ajustes")
cv2.createTrackbar("Oscuridad (sube = detecta mas)", "Ajustes", 30, 255, nada)
cv2.createTrackbar("Color (sube = detecta menos)", "Ajustes", 90, 255, nada)
cv2.createTrackbar("Tamano minimo (sube = ignora chicos)", "Ajustes", 3000, 30000, nada)
cv2.namedWindow("Camara")
cv2.namedWindow("Mascara")
cv2.moveWindow("Camara", 0, 0)
cv2.moveWindow("Mascara", 0, 330)
cv2.moveWindow("Ajustes", 500, 0)
 
historial = deque(maxlen=15)
nivel = 0.0
tiempo_anterior = time.time()
 
fallos = 0
try:
    while True:
        ok, frame = cap.read()
        if not ok:
            fallos += 1
            if fallos > 30:
                print("Se perdió la cámara. Reconectando…")
                estado["camara"] = False
                cap.release()
                cap = abrir_camara()
                fallos = 0
            else:
                time.sleep(0.05)
            estado["arduino"] = arduino_ok if PUERTO else None
            cv2.waitKey(1)   # mantiene las ventanas vivas
            continue
        fallos = 0
        estado["camara"] = True
 
        # ===== DETECTAR PALTAS =====
        alto, ancho = frame.shape[:2]
        area_max = alto * ancho * 0.4
        suave = cv2.GaussianBlur(frame, (9, 9), 0)
        hsv = cv2.cvtColor(suave, cv2.COLOR_BGR2HSV)
 
        v_max = cv2.getTrackbarPos("Oscuridad (sube = detecta mas)", "Ajustes")
        s_min = cv2.getTrackbarPos("Color (sube = detecta menos)", "Ajustes")
        area_min = cv2.getTrackbarPos("Tamano minimo (sube = ignora chicos)", "Ajustes")
 
        con_color = cv2.inRange(hsv, np.array([0, s_min, 0]), np.array([179, 255, 255]))
        oscuros = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([179, 255, v_max]))
        mascara = cv2.bitwise_or(con_color, oscuros)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)
        mascara[:MARGEN, :] = 0
        mascara[-MARGEN:, :] = 0
        mascara[:, :MARGEN] = 0
        mascara[:, -MARGEN:] = 0
 
        contornos, _ = cv2.findContours(mascara, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cantidad = 0
        for c in contornos:
            area = cv2.contourArea(c)
            if area_min < area < area_max:
                cantidad += 1
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
 
        # ===== ESTABILIZAR =====
        historial.append(cantidad)
        paltas = max(set(historial), key=historial.count)
        cv2.putText(frame, "Paltas: " + str(paltas), (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
 
        # ===== SIMULAR NIVEL Y MANEJAR BOMBA =====
        objetivo = min(paltas * ML_POR_PALTA, CAPACIDAD)
        ahora = time.time()
        # mismo tope que ORDEN_VIGENTE_S: si la cámara se trabó menos de 1 s la bomba siguió
        # andando y la simulación lo descuenta; si fue más, el hilo ya la había apagado.
        dt = min(ahora - tiempo_anterior, ORDEN_VIGENTE_S)
        tiempo_anterior = ahora
 
        bomba_encendida = False
        if nivel < objetivo:
            nivel = min(objetivo, nivel + CAUDAL_ML_S * dt)
            bomba_encendida = True
        elif nivel > objetivo:
            nivel = max(objetivo, nivel - CAUDAL_ML_S * dt)
 
        deseo_bomba = bomba_encendida   # la bomba real sigue a la simulación (la envía el hilo)
        ultima_orden = ahora

        estado.update({"paltas": paltas, "nivel": round(nivel, 1), "bomba": bomba_encendida,
                       "arduino": arduino_ok if PUERTO else None,
                       "litros_reales": round(nivel / ML_POR_PALTA * L_REALES_POR_PALTA, 1)})
 
        # ===== MOSTRAR =====
        cv2.imshow("Camara", cv2.resize(frame, (0, 0), fx=ESCALA, fy=ESCALA))
        cv2.imshow("Mascara", cv2.resize(mascara, (0, 0), fx=ESCALA, fy=ESCALA))
 
        k = cv2.waitKey(1)
        if k == ord("q"):
            break
        if k == ord("r"):       # r = reiniciar el nivel a 0 (después de vaciar el tupper a mano)
            nivel = 0.0
finally:
    deseo_bomba = False
    detener.set()                 # el hilo manda '0' y cierra el puerto
    if hilo_serial:
        hilo_serial.join(timeout=3)
    cap.release()
    cv2.destroyAllWindows()
    servidor.shutdown()