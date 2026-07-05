from mega_pi_controller import *
from constants import *
import cv2 
import time

# --- INITIALIZATION AND CONFIGURATION ---
LNM = MegaPiController("/dev/ttyUSB0", 115200)

OPEN_ROI_CENTER = ROI(200, 20, 430, 200) 
ROI_LINES = ROI(200, 300, 440, 350)       
ROI_OBSTACULOS = ROI(30, 30, 610, 320)

running = True

# --- TIMERS Y CONTADORES ---
tiempo_perdida = 0.0
TIEMPO_GRACIA = 0.35  # Margen de seguridad en transiciones seguidas

# --- CONTROLLER DE BLOQUEO (ANTI-VOLTEO) ---
ultimo_freno_time = 0.0
frenos_consecutivos = 0

# --- PARÁMETROS PID NAVEGACIÓN ---
Kp_vision = 0.015    
Ki_vision = 0.0
Kd_vision = 0.035   
prev_error = 0.0
integral = 0.0
MAX_INTEGRAL = 15.0 

# --- PARÁMETROS NAVEGACIÓN OBSTÁCULOS ---
Kp_obstaculo = 0.28   
Kd_obstaculo = 0.01   

# --- CONFIGURACIÓN DE SEPARACIÓN PROPORCIONAL DE PAREDES ---
Kp_pared = 1.6  

# --- MÁQUINA DE ESTADOS ---
# Estados posibles: "LINEAL", "ESQUIVANDO", "RECOMODAR_RECTO"
estado_carrera = "LINEAL"
memoria_lado = None  

# --- CONFIGURACIÓN DE VELOCIDAD Y AJUSTES ---
VELOCIDAD_BASE = 75  
DIST_MIN_CHOQUE = 10.0  
steering_angle = 80     

UMBRAL_PIXELES_MUERTO = 150  
TOLERANCIA_ANGULO = 3        

# --- UMBRALES DE DISTANCIA (Muros Fijos) ---
DIST_DESEADA_PARED = 22.0  
DIST_MIN_PARED = 16.0      
DIST_CRITICA_PARED = 8.5   

# --- ROIs LATERALES ---
roi_izq = ROI(0, 100, 320, 150)  
roi_der = ROI(320, 100, 640, 150)  
roi_izq_inner = ROI(290, 100, 330, 150)  

def obtener_areas_lineas():
    blackcnt_left = LNM.vision.find_contours(LNM.mask_black, roi_izq)
    blackcnt_right = LNM.vision.find_contours(LNM.mask_black, roi_der)

    area_right = LNM.vision.max_contour(blackcnt_right, roi_der)[0]
    LNM.vision.draw_contours(blackcnt_right, roi_der, (0,0,255))

    area_left = LNM.vision.max_contour(blackcnt_left, roi_izq)[0]
    LNM.vision.draw_contours(blackcnt_left, roi_izq, (0,0,255))

    blackcnt_left_avoid = LNM.vision.find_contours(LNM.mask_black, roi_izq_inner)
    area_avoid_left = LNM.vision.max_contour(blackcnt_left_avoid, roi_izq_inner)[0]

    return [area_right, area_left, area_avoid_left]

def procesar_obstaculos():
    cnt_rojo = LNM.vision.find_contours(LNM.mask_red, ROI_OBSTACULOS)
    cnt_verde = LNM.vision.find_contours(LNM.mask_green, ROI_OBSTACULOS)
    datos_rojo = LNM.vision.max_contour(cnt_rojo, ROI_OBSTACULOS)
    datos_verde = LNM.vision.max_contour(cnt_verde, ROI_OBSTACULOS)
    return datos_rojo, datos_verde

def clasificar_escenario_pista(datos_rojo, datos_verde):
    """Identifica el tipo de escenario exacto para evitar predicciones erróneas"""
    area_rojo = datos_rojo[0]
    area_verde = datos_verde[0]
    
    UMBRAL_DETECCION = 200 # Umbral de ruido de píxeles

    # Escenario mixto / Pasar por el medio (Casos 1, 9, 10)
    if area_rojo > UMBRAL_DETECCION and area_verde > UMBRAL_DETECCION:
        return "PASO_CENTRAL"
    # Escenario Pilar Verde (Pasar por la derecha)
    elif area_verde > UMBRAL_DETECCION and area_rojo <= UMBRAL_DETECCION:
        return "PILAR_VERDE"
    # Escenario Pilar Rojo (Pasar por la izquierda)
    elif area_rojo > UMBRAL_DETECCION and area_verde <= UMBRAL_DETECCION:
        return "PILAR_ROJO"
    
    return "LINEAL_CONVENCIONAL"

def draw_all_rois(datos_rojo, datos_verde):
    LNM.vision.draw_roi(roi_izq)
    LNM.vision.draw_roi(roi_der)
    LNM.vision.draw_roi(ROI_OBSTACULOS)
    LNM.vision.draw_roi(roi_izq_inner, (0,0,255))
    if datos_rojo[3] is not None:
        LNM.vision.draw_contours([datos_rojo[3]], ROI_OBSTACULOS, (0, 0, 255)) 
    if datos_verde[3] is not None:
        LNM.vision.draw_contours([datos_verde[3]], ROI_OBSTACULOS, (0, 255, 0)) 

while running:
    try:
        LNM.vision.receive_image()
        LNM.obtener_linea_azul()
        LNM.obtener_linea_naranja()
        LNM.obtenerarea_frontal()
        
        front_dist, left_dist, right_dist, laser_1, laser_2 = LNM.get_distances()
        tof_izq = laser_1
        tof_der = laser_2
        
        black_areas = obtener_areas_lineas()
        datos_rojo, datos_verde = procesar_obstaculos()
        
        # Mapeo predictivo del entorno
        escenario = clasificar_escenario_pista(datos_rojo, datos_verde)
        
        print(f"Estado: {estado_carrera} | Escenario Detectado: {escenario}")
        draw_all_rois(datos_rojo, datos_verde)
        cv2.imshow('Vision HD - Obstacle Challenge', LNM.vision.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # TRACK TYPE DETECTION
        if LNM.turning_direction == 0: 
            if LNM.orange_area > 1200:
                 LNM.turning_direction = 2
            elif LNM.blue_area > 1200:
                 LNM.turning_direction = 1

        # ---------------------------------------------------------------------
        # 🚨 TRIGGER AUTOMÁTICO: RECOMODAR RECTO EN CURVAS (Según image_fe0c10.png)
        # ---------------------------------------------------------------------
        # Si se aproxima un muro lateral de forma crítica o la distancia frontal obliga a romper el giro directo:
        if (front_dist < 45.0 and (left_dist < DIST_CRITICA_PARED or right_dist < DIST_CRITICA_PARED)) and estado_carrera != "RECOMODAR_RECTO":
            print("⚠️ [CURVA DETECTADA] Preparando chasis. Iniciando maniobra de centrado recto hacia atrás.")
            estado_carrera = "RECOMODAR_RECTO"

        if estado_carrera == "RECOMODAR_RECTO":
            LNM.stop(log=False)
            time.sleep(0.1)
            # Retroceder de forma perfectamente alineada (ángulo neutro 80) para ganar espacio de giro limpio
            LNM.move_backward(angle=80, speed=80)
            time.sleep(0.6) 
            LNM.turn_center(log=False)
            
            # Limpiamos variables de control e inercias para abordar la nueva sección desde cero
            prev_error = 0.0
            integral = 0.0
            LNM.vision.reset_stuck_timer()
            estado_carrera = "LINEAL"
            continue

        # ---------------------------------------------------------------------
        # DETECCIÓN DE ATASQUE VISUAL (STALL DETECTION)
        # ---------------------------------------------------------------------
        if LNM.vision.check_if_stuck():
            print("\n🚨 ¡FRENO DE MANO! Carro atrapado mecánicamente.")
            LNM.stop(log=False)
            LNM.move_backward(angle=80, speed=85)
            time.sleep(1.0)
            LNM.turn_center(log=False)
            prev_error = 0.0
            integral = 0.0
            estado_carrera = "LINEAL" 
            tiempo_perdida = 0.0 
            LNM.vision.reset_stuck_timer()
            time.sleep(0.1)
            continue

        # ---------------------------------------------------------------------
        # FRENO DE MANO CONVENCIONAL POR DISTANCIA FRONTAL CRÍTICA
        # ---------------------------------------------------------------------
        if front_dist < DIST_MIN_CHOQUE and front_dist > 1.0:
            current_time = time.time()
            LNM.stop(log=False)
            
            if (current_time - ultimo_freno_time) < 3.0:
                frenos_consecutivos += 1
            else:
                frenos_consecutivos = 1
                
            ultimo_freno_time = current_time
            print(f"🚨 FRENO DE MANO N°{frenos_consecutivos}! Distancia frontal: {front_dist:.1f} cm.")
            
            if frenos_consecutivos >= 2:
                LNM.move_backward(angle=80, speed=85)
                time.sleep(0.9)
                frenos_consecutivos = 0
            else:
                angulo_escape_opuesto = 160 - steering_angle
                angulo_escape_opuesto = max(45, min(115, angulo_escape_opuesto))
                if angulo_escape_opuesto == 80: 
                    angulo_escape_opuesto = 65
                LNM.move_backward(angle=angulo_escape_opuesto, speed=85)
                time.sleep(0.7)
                
            LNM.turn_center(log=False)
            prev_error = 0.0
            integral = 0.0
            estado_carrera = "LINEAL" 
            tiempo_perdida = 0.0 
            LNM.vision.reset_stuck_timer()
            time.sleep(0.1)
            continue

        # ---------------------------------------------------------------------
        # MAQUINA DE ESTADOS REESTRUCTURADA CON CLASIFICACIÓN PREDICTIVA
        # ---------------------------------------------------------------------
        LNM.move_forward(VELOCIDAD_BASE)
        
        # --- ESTADO 1: LINEAL ---
        if estado_carrera == "LINEAL":
            if escenario == "PASO_CENTRAL":
                print("🔀 Transición -> ESQUIVANDO (Doble Obstáculo Detectado - Modo Centro).")
                estado_carrera = "ESQUIVANDO"
                memoria_lado = "CENTRO"
                LNM.vision.reset_stuck_timer()

            elif escenario == "PILAR_VERDE":
                print("🟢 Transición -> ESQUIVANDO (Pilar Verde - Forzar Derecha).")
                estado_carrera = "ESQUIVANDO"
                memoria_lado = "IZQUIERDA"
                LNM.vision.reset_stuck_timer()
                
            elif escenario == "PILAR_ROJO":
                print("🔴 Transición -> ESQUIVANDO (Pilar Rojo - Forzar Izquierda).")
                estado_carrera = "ESQUIVANDO"
                memoria_lado = "DERECHA"
                LNM.vision.reset_stuck_timer()

            if estado_carrera == "LINEAL":
                # Centrado de líneas convencional
                error = black_areas[1] - black_areas[0]
                integral += error
                integral = max(-MAX_INTEGRAL, min(MAX_INTEGRAL, integral))
                derivative = error - prev_error
                correction = (Kp_vision * error) + (Ki_vision * integral) + (Kd_vision * derivative)
                prev_error = error
                
                steering_angle = int(80 + correction)
                steering_angle = max(45, min(115, steering_angle))
                
                if abs(error) < UMBRAL_PIXELES_MUERTO:
                    LNM.turn_center()
                    steering_angle = 80
                elif steering_angle > 80:
                    LNM.turn_right(angle = steering_angle, speed = VELOCIDAD_BASE)
                elif steering_angle < 80:
                    LNM.turn_left(angle = steering_angle, speed = VELOCIDAD_BASE)
        
        # --- ESTADO 2: ESQUIVANDO ---
        elif estado_carrera == "ESQUIVANDO":
            SETPOINT_VERDE = 548
            SETPOINT_ROJO = 51

            if memoria_lado == "CENTRO":
                # Si es un caso doble, calcula el error balanceando la posición de los dos chasis detectados
                centro_obstaculos = (datos_verde[1] + datos_rojo[1]) // 2
                error_obs = centro_obstaculos - 320 # 320 es la mitad exacta de tus 640 de resolución
                if datos_verde[0] < 150 and datos_rojo[0] < 150:
                    estado_carrera = "LINEAL"
                    memoria_lado = ""

            elif memoria_lado == "IZQUIERDA":
                error_obs = datos_verde[1] - SETPOINT_VERDE
                if tiempo_perdida == 0.0:
                    tiempo_perdida = time.time()
                elif (time.time() - tiempo_perdida) > TIEMPO_GRACIA:
                    estado_carrera = "LINEAL"
                    tiempo_perdida = 0.0
                    memoria_lado = ""
                    LNM.vision.reset_stuck_timer()
            else:
                error_obs = datos_rojo[1] - SETPOINT_ROJO
                if tiempo_perdida == 0.0:
                    tiempo_perdida = time.time()
                elif (time.time() - tiempo_perdida) > 0.51:
                    estado_carrera = "LINEAL"
                    tiempo_perdida = 0.0
                    memoria_lado = ""
                    LNM.vision.reset_stuck_timer()

            derivative_obs = error_obs - prev_error
            correction_obs = (Kp_obstaculo * error_obs) + (Kd_obstaculo * derivative_obs)
            prev_error = error_obs

            steering_angle = int(80 + correction_obs)
            steering_angle = max(40, min(120, steering_angle))

            if (black_areas[2] > 100) and memoria_lado == "IZQUIERDA":
                    LNM.turn_right(120, speed = VELOCIDAD_BASE + 30)
                    continue
            if steering_angle > 80:
                LNM.turn_right(angle = steering_angle, speed = VELOCIDAD_BASE)
            elif steering_angle < 80:
                LNM.turn_left(angle = steering_angle, speed = VELOCIDAD_BASE)
                
    except Exception as e:
        print("Error crítico ejecutando el bucle:", e)
        break

LNM.stop()
cv2.destroyAllWindows()
