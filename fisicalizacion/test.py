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
 
# ---------- Arduino ----------
arduino = None
ultimo_intento = 0
 
def conectar():
    global arduino
    try:
        arduino = serial.Serial(PUERTO, 9600, timeout=0, write_timeout=0.3)
        time.sleep(2)   # el Arduino necesita un momento al conectarse
        print("Arduino conectado en", PUERTO)
    except Exception as e:
        arduino = None
        print("No se pudo abrir", PUERTO, "->", e)
 
def bomba(encender):
    global arduino, ultimo_intento
    if not PUERTO:
        return
    if arduino is None:          # si no hay conexión, reintenta cada 3 segundos
        if time.time() - ultimo_intento > 3:
            ultimo_intento = time.time()
            conectar()
        return
    try:
        arduino.write(b"1" if encender else b"0")
    except Exception as e:
        print("FALLO al hablar con el Arduino:", e)
        arduino = None
 
if PUERTO:
    conectar()
    if arduino is None:
        print("Sigo SIN Arduino por ahora (reintentaré solo). Cierra el Monitor Serie del IDE si lo tienes abierto.")
 
# ---------- Servidor web (sirve index.html y el estado) ----------
estado = {"paltas": 0, "nivel": 0, "capacidad": CAPACIDAD, "bomba": False,
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
cap = cv2.VideoCapture(URL)
if not cap.isOpened():
    print("No se pudo abrir la cámara. Revisa la IP y que el servidor esté iniciado.")
    exit()
 
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
                print("Se perdió la cámara")
                break
            time.sleep(0.05)
            continue
        fallos = 0
 
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
        dt = min(ahora - tiempo_anterior, 0.2)
        tiempo_anterior = ahora
 
        bomba_encendida = False
        if nivel < objetivo:
            nivel = min(objetivo, nivel + CAUDAL_ML_S * dt)
            bomba_encendida = True
        elif nivel > objetivo:
            nivel = max(objetivo, nivel - CAUDAL_ML_S * dt)
 
        bomba(bomba_encendida)   # la bomba real sigue a la simulación
 
        estado.update({"paltas": paltas, "nivel": round(nivel, 1), "bomba": bomba_encendida,
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
    bomba(False)
    if arduino:
        arduino.close()
    cap.release()
    cv2.destroyAllWindows()
    servidor.shutdown()