from mega_pi_controller import *
from constants import *
import cv2 
import time

# --- INITIALIZATION AND CONFIGURATION ---
LNM = MegaPiController("/dev/ttyUSB0", 115200)

# Sobrescribimos/Añadimos las ROIs necesarias para obstáculos en este archivo
OPEN_ROI_CENTER = ROI(200, 20, 430, 200) # Tu ROI frontal original
ROI_LINES = ROI(200, 300, 440, 350)       # Tu ROI de líneas original

# NUEVA ROI: Enfocada en el carril central medio para detectar pilares a tiempo
ROI_OBSTACULOS = ROI(30, 30, 610, 320)

while not LNM.start():
    pass
running = True

# --- TIMERS Y CONTADORES ---
orange_timer = time.time()
blue_timer = time.time()
loops = 0
n = 0
girando = False  # Inicialización de la bandera de esquinas cerradas

# --- VARIABLES PARA TIEMPO DE GRACIA ---
tiempo_perdida = 0.0
TIEMPO_GRACIA = 0.2  # Segundos extra que mantendrá el giro tras perder el pilar de vista

# --- PARÁMETROS PID PARA CENTRADO DE LÍNEAS (Ronda Abierta) ---
Kp_vision = 0.015    
Ki_vision = 0.0
Kd_vision = 0.035   
prev_error = 0.0
integral = 0.0
MAX_INTEGRAL = 15.0 

# --- PARÁMETROS PID EXCLUSIVOS PARA EVITAR OBSTÁCULOS ---
Kp_obstaculo = 0.28   # Más agresivo porque el rango de error en píxeles es menor
Kd_obstaculo = 0.01   # Amortigua el giro para evitar que la cola derrape y toque el pilar

# --- MÁQUINA DE ESTADOS PARA OBSTÁCULOS ---
estado_carrera = "LINEAL"
memoria_lado = None  # Guardará "IZQUIERDA" o "DERECHA"

# --- CONFIGURACIÓN DE VELOCIDAD Y AJUSTES (MODERADA A 65) ---
VELOCIDAD_BASE = 75
DIST_MIN_CHOQUE = 12.0  
steering_angle = 80     

UMBRAL_PIXELES_MUERTO = 150  
TOLERANCIA_ANGULO = 3       

# --- CONFIGURACIÓN PARA EVITAR PAREDES SEGUIDAS ---
DIST_MIN_PARED = 18.0  # Si un lateral mide menos de esto, se está encajonando contra la pared

# --- FIN DE CARRERA ---
end_game_triggered = False
end_game_timer = 0.0

# --- ROIs LATERALES (Para centrado lineal) ---
roi_izq = ROI(0, 100, 320, 150)  
roi_der = ROI(320, 100, 640, 150)  

# --- HELPERS LOCALES ---
def obtener_areas_lineas():
    blackcnt_left = LNM.vision.find_contours(LNM.mask_black, roi_izq)
    blackcnt_right = LNM.vision.find_contours(LNM.mask_black, roi_der)
    area_right = LNM.vision.max_contour(blackcnt_right, roi_der)[0]
    area_left = LNM.vision.max_contour(blackcnt_left, roi_izq)[0]
    return [area_right, area_left]

def procesar_obstaculos():
    """Busca pilares rojos y verdes en la nueva ROI_OBSTACULOS"""
    cnt_rojo = LNM.vision.find_contours(LNM.mask_red, ROI_OBSTACULOS)
    cnt_verde = LNM.vision.find_contours(LNM.mask_green, ROI_OBSTACULOS)
    
    datos_rojo = LNM.vision.max_contour(cnt_rojo, ROI_OBSTACULOS)
    datos_verde = LNM.vision.max_contour(cnt_verde, ROI_OBSTACULOS)
    print(f"🔴 Rojo: Área={datos_rojo[0]}, X={datos_rojo[1]}, Y={datos_rojo[2]}")
    print(f"🟢 Verde: Área={datos_verde[0]}, X={datos_verde[1]}, Y={datos_verde[2]}")
    
    return datos_rojo, datos_verde

def draw_all_rois(datos_rojo, datos_verde):
    """Dibuja en pantalla para telemetría visual"""
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
        # 1. Adquisición de imágenes y telemetría de sensores estándar
        LNM.vision.receive_image()
        LNM.obtener_linea_azul()
        LNM.obtener_linea_naranja()
        LNM.obtenerarea_frontal()
        
        # Distancias físicas de los ultrasonidos
        front_dist, left_dist, right_dist = LNM.get_distances()
        
        # Procesar datos de visión localizados
        black_areas = obtener_areas_lineas()
        datos_rojo, datos_verde = procesar_obstaculos()
        
        # Dibujar elementos en el frame
        draw_all_rois(datos_rojo, datos_verde)
        cv2.imshow('Vision HD - Obstacle Challenge', LNM.vision.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # =========================================================================
        # FRENO DE MANO DE EMERGENCIA
        # =========================================================================
        if front_dist < DIST_MIN_CHOQUE and front_dist > 1.0:
            print(f"🚨 ¡FRENO DE MANO! Frente obstruido a {front_dist:.2f} cm.")
            LNM.stop(log=False)
            time.sleep(0.05)
            
            angulo_escape_opuesto = 160 - steering_angle
            angulo_escape_opuesto = max(40, min(120, angulo_escape_opuesto))
            if angulo_escape_opuesto == 80:
                angulo_escape_opuesto = 60
                
            LNM.move_backward(angle=angulo_escape_opuesto, speed=85)
            time.sleep(0.75)
            LNM.turn_center(log=False)
            prev_error = 0.0
            integral = 0.0
            estado_carrera = "LINEAL" 
            girando = False
            tiempo_perdida = 0.0 # Reset de seguridad
            time.sleep(0.1)
            continue

        # Mantenemos la velocidad constante
        LNM.move_forward(speed=VELOCIDAD_BASE) 

        # Detección del sentido de la pista (Líneas de las esquinas)
        if LNM.turning_direction == 0: 
            if LNM.orange_area > 1200:
                 LNM.turning_direction = 2
            elif LNM.blue_area > 1200:
                 LNM.turning_direction = 1

        # =========================================================================
        # MÁQUINA DE ESTADOS: NAVEGACIÓN Y EVASIÓN DE OBSTÁCULOS
        # =========================================================================
        
        # --- ESTADO 1: LINEAL (Centrado de líneas + Giros controlados en Esquinas) ---
        if estado_carrera == "LINEAL":
            
            if datos_verde[0] > 350 and datos_verde[0] >= datos_rojo[0]:
                print("🟢 ¡Pilar Verde Detectado! Cambiando a ESQUIVANDO.")
                estado_carrera = "ESQUIVANDO"
                memoria_lado = "IZQUIERDA" 
                prev_error = 0.0
                tiempo_perdida = 0.0
                girando = False 
            elif datos_rojo[0] > 300 and datos_rojo[0] > datos_verde[0]:
                print("🔴 ¡Pilar Rojo Detectado! Cambiando a ESQUIVANDO.")
                estado_carrera = "ESQUIVANDO"
                memoria_lado = "DERECHA"   
                prev_error = 0.0
                tiempo_perdida = 0.0
                girando = False 

            # --- CONTROL DE GIROS EN ESQUINAS CERRADAS ---
            if estado_carrera == "LINEAL":
                if front_dist < 90 and not girando and LNM.black_area > 8000 and LNM.turning_direction != 0:
                    print("↩️ [ESQUINA] Detectada curva cerrada. Forzando giro de esquina.")
                    LNM.turn_direction()
                    girando = True
                    
                elif LNM.black_area < 8000 and girando and front_dist > 80:
                    print("➡️ [ESQUINA] Pista liberada. Centrando dirección.")
                    LNM.turn_center()
                    girando = False
                    steering_angle = 80

                # Ejecución de PID de líneas estándar
                if not girando:
                    error = black_areas[1] - black_areas[0]
                    integral += error
                    integral = max(-MAX_INTEGRAL, min(MAX_INTEGRAL, integral))
                    derivative = error - prev_error
                    correction = (Kp_vision * error) + (Ki_vision * integral) + (Kd_vision * derivative)
                    prev_error = error
                    
                    steering_angle = int(80 + correction)
                    steering_angle = max(40, min(120, steering_angle))
                    
                    if abs(error) < UMBRAL_PIXELES_MUERTO or abs(steering_angle - 80) <= TOLERANCIA_ANGULO:
                        LNM.turn_center()
                        steering_angle = 80
                    elif steering_angle > 80:
                        LNM.turn_right(angle=steering_angle, speed=VELOCIDAD_BASE)
                    elif steering_angle < 80:
                        LNM.turn_left(angle=steering_angle, speed=VELOCIDAD_BASE)

        # --- ESTADO 2: ESQUIVANDO ---
        elif estado_carrera == "ESQUIVANDO":
            print(f"🔄 [MODO ESQUIVA]: Evadiendo pilar por la {memoria_lado} | L:{left_dist}cm R:{right_dist}cm")
            
            # SETPOINTS ABSOLUTOS EN PÍXELES
            SETPOINT_VERDE = 548
            SETPOINT_ROJO = 51
            
            # DETECCIÓN DE ENCAJONAMIENTO TOTAL VIA ULTRASONIDOS
            if memoria_lado == "IZQUIERDA" and left_dist < DIST_MIN_PARED and left_dist > 1.0:
                print("⚠️ Pared izquierda encima. Forzando REBASANDO.")
                estado_carrera = "REBASANDO"
                continue
            elif memoria_lado == "DERECHA" and right_dist < DIST_MIN_PARED and right_dist > 1.0:
                print("⚠️ Pared derecha encima. Forzando REBASANDO.")
                estado_carrera = "REBASANDO"
                continue
            
            if memoria_lado == "IZQUIERDA": 
                if datos_verde[0] == 0:
                    if tiempo_perdida == 0.0:
                        tiempo_perdida = time.time()  # Inicia el contador
                    elif (time.time() - tiempo_perdida) > TIEMPO_GRACIA:
                        estado_carrera = "REBASANDO"
                        tiempo_perdida = 0.0
                        continue
                    
                    print(f"⏳ [GRACIA] Manteniendo evasión izquierda por {TIEMPO_GRACIA}s...")
                    error_obs = prev_error  # Mantiene la inercia del cálculo PID anterior
                else:
                    tiempo_perdida = 0.0  # Resetea si vuelve a ver el pilar intermitentemente
                    error_obs = datos_verde[1] - SETPOINT_VERDE
                
            else: 
                if datos_rojo[0] == 0:
                    if tiempo_perdida == 0.0:
                        tiempo_perdida = time.time()  # Inicia el contador
                    elif (time.time() - tiempo_perdida) > TIEMPO_GRACIA:
                        estado_carrera = "REBASANDO"
                        tiempo_perdida = 0.0
                        continue
                    
                    print(f"⏳ [GRACIA] Manteniendo evasión derecha por {TIEMPO_GRACIA}s...")
                    error_obs = prev_error  # Mantiene la inercia del cálculo PID anterior
                else:
                    tiempo_perdida = 0.0  # Resetea
                    error_obs = datos_rojo[1] - SETPOINT_ROJO
            
            # --- CÁLCULO PID ---
            derivative_obs = error_obs - prev_error
            correction_obs = (Kp_obstaculo * error_obs) + (Kd_obstaculo * derivative_obs)
            prev_error = error_obs
            
            steering_angle = int(80 + correction_obs)
            steering_angle = max(40, min(120, steering_angle))
            
            if steering_angle > 80:
                LNM.turn_right(angle=steering_angle, speed=VELOCIDAD_BASE)
            elif steering_angle < 80:
                LNM.turn_left(angle=steering_angle, speed=VELOCIDAD_BASE)

        # --- ESTADO 3: REBASANDO ---
        elif estado_carrera == "REBASANDO":
            print(f"⏱️ [MODO REBASE]: Esperando liberación lateral. L:{left_dist}cm | R:{right_dist}cm")
            
            if memoria_lado == "IZQUIERDA":
                if left_dist < DIST_MIN_PARED and left_dist > 1.0:
                    LNM.turn_right(angle=85, speed=VELOCIDAD_BASE) 
                else:
                    LNM.turn_left(angle=72, speed=VELOCIDAD_BASE)  
                
                if right_dist > 40:
                    print("✅ Pilar verde superado por completo.")
                    estado_carrera = "LINEAL"
                    prev_error = 0.0
            
            elif memoria_lado == "DERECHA":
                if right_dist < DIST_MIN_PARED and right_dist > 1.0:
                    LNM.turn_left(angle=75, speed=VELOCIDAD_BASE)  
                else:
                    LNM.turn_right(angle=88, speed=VELOCIDAD_BASE) 
                
                if left_dist > 40:
                    print("✅ Pilar rojo superado por completo.")
                    estado_carrera = "LINEAL"
                    prev_error = 0.0

    except Exception as e:
        print("Exception en el bucle principal:", e)
        LNM.stop()
        break

# --- SAFETY SHUTDOWN ---
LNM.stop()
