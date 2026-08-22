from mega_pi_controller import *
from constants import *
import cv2 
import time

# --- INITIALIZATION AND CONFIGURATION ---
LNM = MegaPiController("/dev/ttyUSB0", 115200)

OPEN_ROI_CENTER = ROI(200, 20, 430, 200) 
ROI_LINES = ROI(200, 300, 440, 350)       
ROI_OBSTACULOS = ROI(30, 30, 610, 320)

while not LNM.start():
    pass
running = True

# --- TIMERS Y CONTADORES ---
loops = 0
girando = False  

# --- PAR�METROS DE EVASI�N PROPORCIONAL Y F�SICA ---
# En lugar de un setpoint en p�xeles, usamos el �rea. 
# A mayor �rea (pilar m�s cerca), mayor es el factor de giro.
K_EVASION = 0.004  
TIEMPO_LIBERACION_COLA = 0.35 # Segundos para que la rueda trasera pase tras perder el pilar. Ajustar con t = d/v.
timer_cola = 0.0
esperando_cola = False

# --- PAR�METROS PID L�NEAS ---
Kp_vision = 0.015    
Ki_vision = 0.0
Kd_vision = 0.035   
prev_error = 0.0
integral = 0.0
MAX_INTEGRAL = 15.0 

# --- CONFIGURACI�N DE VELOCIDAD ---
VELOCIDAD_BASE = 68
DIST_MIN_CHOQUE = 12.0  
UMBRAL_AREA_EVASION = 400 # �rea m�nima para considerar que es un pilar real
DIST_DETECCION_LATERAL = 25.0 # Distancia a la que el sensor lateral "ve" el pilar al pasar

estado_carrera = "LINEAL"
memoria_lado = None  

roi_izq = ROI(0, 100, 320, 150)  
roi_der = ROI(320, 100, 640, 150)  

def obtener_areas_lineas():
    blackcnt_left = LNM.vision.find_contours(LNM.mask_black, roi_izq)
    blackcnt_right = LNM.vision.find_contours(LNM.mask_black, roi_der)
    area_right = LNM.vision.max_contour(blackcnt_right, roi_der)[0]
    area_left = LNM.vision.max_contour(blackcnt_left, roi_izq)[0]
    return [area_right, area_left]

def procesar_obstaculos():
    cnt_rojo = LNM.vision.find_contours(LNM.mask_red, ROI_OBSTACULOS)
    cnt_verde = LNM.vision.find_contours(LNM.mask_green, ROI_OBSTACULOS)
    return LNM.vision.max_contour(cnt_rojo, ROI_OBSTACULOS), LNM.vision.max_contour(cnt_verde, ROI_OBSTACULOS)

def draw_all_rois(datos_rojo, datos_verde):
    LNM.vision.draw_roi(roi_izq)
    LNM.vision.draw_roi(roi_der)
    LNM.vision.draw_roi(ROI_OBSTACULOS)
    if datos_rojo[3] is not None:
        LNM.vision.draw_contours([datos_rojo[3]], ROI_OBSTACULOS, (0, 0, 255)) 
    if datos_verde[3] is not None:
        LNM.vision.draw_contours([datos_verde[3]], ROI_OBSTACULOS, (0, 255, 0)) 

# --- MAIN CONTROL LOOP ---
while running:
    try:
        LNM.vision.receive_image()
        LNM.obtener_linea_azul()
        LNM.obtener_linea_naranja()
        LNM.obtenerarea_frontal()
        
        front_dist, left_dist, right_dist = LNM.get_distances()
        black_areas = obtener_areas_lineas()
        datos_rojo, datos_verde = procesar_obstaculos()

        print("front:", LNM.dist_front, "left:", LNM.dist_left, "right:", LNM.dist_right)
        
        draw_all_rois(datos_rojo, datos_verde)
        cv2.imshow('Vision HD - K-O-M-R-A-D', LNM.vision.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # --- FRENO DE EMERGENCIA ---
        if 1.0 < front_dist < DIST_MIN_CHOQUE:
            print("?? �FRENO DE MANO!")
            LNM.stop(log=False)
            time.sleep(0.05)
            LNM.move_backward(angle=80, speed=85) # Retroceso recto de seguridad
            time.sleep(0.75)
            LNM.turn_center(log=False)
            estado_carrera = "LINEAL" 
            girando = False
            esperando_cola = False
            continue

        LNM.move_forward(speed=VELOCIDAD_BASE) 

        if LNM.turning_direction == 0: 
            if LNM.orange_area > 1200: LNM.turning_direction = 2
            elif LNM.blue_area > 1200: LNM.turning_direction = 1

        # =========================================================================
        # M�QUINA DE ESTADOS F�SICA
        # =========================================================================
        
        # --- ESTADO 1: LINEAL ---
        if estado_carrera == "LINEAL":
            area_verde = datos_verde[0]
            area_roja = datos_rojo[0]
            
            
            # Disparador por �rea (ignora la distorsi�n del borde del lente)
            if area_verde > UMBRAL_AREA_EVASION and area_verde >= area_roja:
                estado_carrera = "ESQUIVANDO"
                memoria_lado = "VERDE_DERECHA" # El pilar verde se esquiva por la izquierda
            elif area_roja > UMBRAL_AREA_EVASION and area_roja > area_verde:
                estado_carrera = "ESQUIVANDO"
                memoria_lado = "ROJO_IZQUIERDA" # El pilar rojo se esquiva por la derecha

            # L�gica de esquinas intacta
            if estado_carrera == "LINEAL":
                if front_dist < 90 and not girando and LNM.black_area > 8000 and LNM.turning_direction != 0:
                    LNM.turn_direction()
                    girando = True
                elif LNM.black_area < 8000 and girando and front_dist > 80:
                    LNM.turn_center()
                    girando = False

                if not girando:
                    error = black_areas[1] - black_areas[0]
                    integral = max(-MAX_INTEGRAL, min(MAX_INTEGRAL, integral + error))
                    derivative = error - prev_error
                    correction = (Kp_vision * error) + (Ki_vision * integral) + (Kd_vision * derivative)
                    prev_error = error
                    
                    steering_angle = int(80 + correction)
                    steering_angle = max(40, min(120, steering_angle))
                    
                    if abs(error) < 150: LNM.turn_center()
                    elif steering_angle > 80: LNM.turn_right(angle=steering_angle, speed=VELOCIDAD_BASE)
                    elif steering_angle < 80: LNM.turn_left(angle=steering_angle, speed=VELOCIDAD_BASE)

        # --- ESTADO 2: ESQUIVANDO (Giro Proporcional) ---
        elif estado_carrera == "ESQUIVANDO":
            # Si el sensor lateral de ese lado ve el pilar, pasamos al siguiente estado
            if memoria_lado == "VERDE_DERECHA" and 1.0 < right_dist < DIST_DETECCION_LATERAL:
                estado_carrera = "REBASANDO"
                esperando_cola = False
                continue
            elif memoria_lado == "ROJO_IZQUIERDA" and 1.0 < left_dist < DIST_DETECCION_LATERAL:
                estado_carrera = "REBASANDO"
                esperando_cola = False
                continue

            # C�lculo proporcional: Entre m�s grande el �rea, m�s agresivo el giro
            if memoria_lado == "VERDE_DERECHA":
                area = datos_verde[0]
                evasion_offset = int(area * K_EVASION)
                steering_angle = max(40, 80 - evasion_offset) # Gira a la izquierda
                LNM.turn_left(angle=steering_angle, speed=VELOCIDAD_BASE)
                
            elif memoria_lado == "ROJO_IZQUIERDA":
                area = datos_rojo[0]
                evasion_offset = int(area * K_EVASION)
                steering_angle = min(120, 80 + evasion_offset) # Gira a la derecha
                LNM.turn_right(angle=steering_angle, speed=VELOCIDAD_BASE)

        # --- ESTADO 3: REBASANDO (Retraso Cinem�tico Ackermann) ---
        elif estado_carrera == "REBASANDO":
            # 1. Suavizamos el �ngulo para ir en paralelo, no volvemos bruscamente
            if memoria_lado == "VERDE_DERECHA": LNM.turn_left(angle=75, speed=VELOCIDAD_BASE)
            else: LNM.turn_right(angle=85, speed=VELOCIDAD_BASE)

            # 2. Gatillo de liberaci�n: El sensor lateral deja de ver el pilar
            if not esperando_cola:
                if (memoria_lado == "VERDE_DERECHA" and right_dist > DIST_DETECCION_LATERAL) or \
                   (memoria_lado == "ROJO_IZQUIERDA" and left_dist > DIST_DETECCION_LATERAL):
                    esperando_cola = True
                    timer_cola = time.time()
                    print("?? Pilar sali� del sensor lateral. Calculando espacio para cola...")
            
            # 3. Temporizador no bloqueante: Esperamos que la rueda trasera pase
            else:
                if time.time() - timer_cola > TIEMPO_LIBERACION_COLA:
                    print("? Cola libre. Retornando a control LINEAL.")
                    estado_carrera = "LINEAL"
                    prev_error = 0.0

    except Exception as e:
        print("Exception:", e)
        LNM.stop()
        break

LNM.stop()